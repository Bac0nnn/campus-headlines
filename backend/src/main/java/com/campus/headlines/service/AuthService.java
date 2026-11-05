package com.campus.headlines.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.campus.headlines.common.BusinessException;
import com.campus.headlines.dto.LoginVO;
import com.campus.headlines.dto.MediaLoginRequest;
import com.campus.headlines.dto.PasswordLoginRequest;
import com.campus.headlines.dto.PhoneLoginRequest;
import com.campus.headlines.dto.ProfileUpdateRequest;
import com.campus.headlines.dto.RegisterRequest;
import com.campus.headlines.entity.ApUser;
import com.campus.headlines.entity.WmUser;
import com.campus.headlines.mapper.ApUserMapper;
import com.campus.headlines.mapper.WmUserMapper;
import com.campus.headlines.utils.JwtUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 统一认证：普通用户、作者、审核员共用 ap_user；作者/审核员额外关联 wm_user。
 */
@Service
@RequiredArgsConstructor
public class AuthService {

    private final ApUserMapper apUserMapper;
    private final WmUserMapper wmUserMapper;
    private final JwtUtils jwtUtils;
    private final PasswordEncoder passwordEncoder;

    public Map<String, Object> sendCode(String phone) {
        if (phone == null || !phone.matches("^1\\d{10}$")) {
            throw new BusinessException("手机号格式不正确");
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("message", "验证码已发送，开发环境固定为 123456");
        result.put("expireSeconds", 60);
        return result;
    }

    /** 验证码登录 */
    @Transactional
    public LoginVO login(PhoneLoginRequest request) {
        if (!"123456".equals(request.getCode())) {
            throw new BusinessException("验证码错误，开发环境请输入 123456");
        }
        ApUser user = findByPhone(request.getPhone());
        if (user == null) {
            user = new ApUser();
            user.setPhone(request.getPhone());
            user.setPassword(passwordEncoder.encode("123456"));
            user.setNickname("校园用户" + request.getPhone().substring(7));
            user.setRole(0);
            user.setAvatar("/avatars/u1.svg");
            user.setBio("这个人很懒，还没有填写个人简介");
            user.setGender(0);
            user.setStatus(1);
            apUserMapper.insert(user);
        }
        return buildLoginVO(user, true);
    }

    /** 注册：普通用户 / 作者 / 审核员 */
    @Transactional
    public LoginVO register(RegisterRequest request) {
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new BusinessException("两次输入的密码不一致");
        }
        if (findByPhone(request.getPhone()) != null) {
            throw new BusinessException("该手机号已注册，请直接登录");
        }
        int role = request.getRole() == null ? 0 : request.getRole();
        String encoded = passwordEncoder.encode(request.getPassword());

        ApUser user = new ApUser();
        user.setPhone(request.getPhone());
        user.setNickname(request.getNickname().trim());
        user.setPassword(encoded);
        user.setRole(role);
        user.setAvatar("/avatars/u" + ((Math.abs(request.getPhone().hashCode()) % 12) + 1) + ".svg");
        user.setBio("这个人很懒，还没有填写个人简介");
        user.setGender(0);
        user.setStatus(1);
        apUserMapper.insert(user);

        if (role > 0) {
            WmUser wm = new WmUser();
            wm.setApUserId(user.getId());
            wm.setUsername(user.getPhone());
            wm.setPassword(encoded);
            wm.setName(user.getNickname());
            wm.setAvatar(user.getAvatar());
            wm.setIntro(role == 2 ? "校园头条审核员" : "校园头条作者");
            wm.setRole(role == 2 ? 1 : 0);
            wm.setStatus(1);
            wmUserMapper.insert(wm);
        }
        return buildLoginVO(user, true);
    }

    /** 手机号 + 密码登录（普通用户 / 作者 / 审核员均可） */
    public LoginVO loginByPassword(PasswordLoginRequest request) {
        ApUser user = findByPhone(request.getPhone());
        if (user == null || !StringUtils.hasText(user.getPassword())
                || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException("手机号或密码错误");
        }
        if (user.getStatus() == null || user.getStatus() != 1) {
            throw new BusinessException("账号已被禁用，请联系管理员");
        }
        return buildLoginVO(user, true);
    }

    /**
     * 创作中心登录：支持手机号 + 密码（推荐），兼容原有 username + 密码。
     */
    public LoginVO loginMedia(MediaLoginRequest request) {
        String account = request.getUsername();
        ApUser apUser = findByPhone(account);
        if (apUser != null) {
            if (!passwordEncoder.matches(request.getPassword(), apUser.getPassword())) {
                throw new BusinessException("手机号或密码错误");
            }
            if (apUser.getRole() == null || apUser.getRole() == 0) {
                throw new BusinessException("该账号是普通用户，请从用户端登录");
            }
            return buildLoginVO(apUser, true);
        }

        WmUser wmUser = wmUserMapper.selectOne(new LambdaQueryWrapper<WmUser>()
                .eq(WmUser::getUsername, account));
        if (wmUser == null || !passwordEncoder.matches(request.getPassword(), wmUser.getPassword())) {
            throw new BusinessException("账号或密码错误");
        }
        if (wmUser.getStatus() == null || wmUser.getStatus() != 1) {
            throw new BusinessException("账号已被禁用，请联系管理员");
        }
        ApUser linked = wmUser.getApUserId() == null ? null : apUserMapper.selectById(wmUser.getApUserId());
        if (linked == null) {
            throw new BusinessException("账号未关联用户信息，请联系管理员");
        }
        return buildLoginVO(linked, true);
    }

    public LoginVO me(Long userId) {
        ApUser user = apUserMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(401, "用户不存在");
        }
        return buildLoginVO(user, false);
    }

    /** 修改个人资料，作者/审核员同步更新媒体号名称与头像 */
    @Transactional
    public LoginVO updateProfile(Long userId, ProfileUpdateRequest request) {
        ApUser user = apUserMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(401, "用户不存在");
        }
        user.setNickname(request.getNickname().trim());
        user.setBio(request.getBio());
        if (request.getGender() != null && request.getGender() >= 0 && request.getGender() <= 2) {
            user.setGender(request.getGender());
        }
        if (StringUtils.hasText(request.getAvatar())) {
            user.setAvatar(request.getAvatar());
        }
        apUserMapper.updateById(user);

        WmUser wm = findWm(user.getId());
        if (wm != null) {
            wm.setName(user.getNickname());
            wm.setAvatar(user.getAvatar());
            wmUserMapper.updateById(wm);
        }
        return buildLoginVO(user, false);
    }

    /** 头像二进制保存到 ap_user.avatar_data */
    @Transactional
    public LoginVO uploadAvatar(Long userId, MultipartFile file) {
        ApUser user = apUserMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(401, "用户不存在");
        }
        if (file == null || file.isEmpty()) {
            throw new BusinessException("请选择头像图片");
        }
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new BusinessException("头像不能超过 5MB");
        }
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new BusinessException("仅支持图片格式");
        }
        try {
            user.setAvatarData(file.getBytes());
            user.setAvatarType(contentType);
            user.setAvatar("/api/auth/avatar/" + userId + "?v="
                    + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss")));
            apUserMapper.updateById(user);
            WmUser wm = findWm(userId);
            if (wm != null) {
                wm.setAvatar(user.getAvatar());
                wmUserMapper.updateById(wm);
            }
            return buildLoginVO(user, false);
        } catch (Exception e) {
            throw new BusinessException("头像上传失败，请重试");
        }
    }

    public AvatarData getAvatar(Long userId) {
        ApUser user = apUserMapper.selectById(userId);
        if (user == null || user.getAvatarData() == null || user.getAvatarData().length == 0) {
            throw new BusinessException(404, "头像不存在");
        }
        return new AvatarData(user.getAvatarData(), user.getAvatarType());
    }

    private ApUser findByPhone(String phone) {
        return apUserMapper.selectOne(new LambdaQueryWrapper<ApUser>()
                .eq(ApUser::getPhone, phone));
    }

    private WmUser findWm(Long apUserId) {
        return wmUserMapper.selectOne(new LambdaQueryWrapper<WmUser>()
                .eq(WmUser::getApUserId, apUserId));
    }

    private LoginVO buildLoginVO(ApUser user, boolean withToken) {
        Integer userRole = user.getRole() == null ? 0 : user.getRole();
        WmUser wm = userRole > 0 ? findWm(user.getId()) : null;
        Long wmUserId = wm == null ? null : wm.getId();
        String token = null;
        if (withToken) {
            token = jwtUtils.createToken(user.getId(), userRole > 0 ? "MEDIA" : "USER",
                    user.getNickname(), userRole, wmUserId);
        }
        return LoginVO.builder()
                .token(token)
                .id(user.getId())
                .name(user.getNickname())
                .avatar(user.getAvatar())
                .role(userRole > 0 ? "MEDIA" : "USER")
                .userRole(userRole)
                .wmUserId(wmUserId)
                .accountRole(wm == null ? null : wm.getRole())
                .account(user.getPhone())
                .bio(user.getBio())
                .gender(user.getGender())
                .build();
    }

    public record AvatarData(byte[] data, String contentType) {
    }
}

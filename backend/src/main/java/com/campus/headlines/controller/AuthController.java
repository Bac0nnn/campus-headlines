package com.campus.headlines.controller;

import com.campus.headlines.common.Result;
import com.campus.headlines.dto.LoginVO;
import com.campus.headlines.dto.PasswordLoginRequest;
import com.campus.headlines.dto.PhoneLoginRequest;
import com.campus.headlines.dto.ProfileUpdateRequest;
import com.campus.headlines.dto.RegisterRequest;
import com.campus.headlines.service.AuthService;
import com.campus.headlines.utils.UserContext;
import lombok.RequiredArgsConstructor;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import javax.validation.Valid;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/send-code")
    public Result<Map<String, Object>> sendCode(@RequestParam String phone) {
        return Result.ok(authService.sendCode(phone));
    }

    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody PhoneLoginRequest request) {
        return Result.ok(authService.login(request));
    }

    @PostMapping("/login/password")
    public Result<LoginVO> loginByPassword(@Valid @RequestBody PasswordLoginRequest request) {
        return Result.ok(authService.loginByPassword(request));
    }

    @PostMapping("/register")
    public Result<LoginVO> register(@Valid @RequestBody RegisterRequest request) {
        return Result.ok(authService.register(request));
    }

    @GetMapping("/me")
    public Result<LoginVO> me() {
        return Result.ok(authService.me(UserContext.userId()));
    }

    @PutMapping("/profile")
    public Result<LoginVO> updateProfile(@Valid @RequestBody ProfileUpdateRequest request) {
        return Result.ok(authService.updateProfile(UserContext.userId(), request));
    }

    /** 上传头像，二进制写入 ap_user.avatar_data */
    @PostMapping("/avatar")
    public Result<LoginVO> uploadAvatar(@RequestParam("file") MultipartFile file) {
        return Result.ok(authService.uploadAvatar(UserContext.userId(), file));
    }

    /** 从数据库读取头像 */
    @GetMapping("/avatar/{id}")
    public ResponseEntity<byte[]> avatar(@PathVariable Long id) {
        AuthService.AvatarData data = authService.getAvatar(id);
        String contentType = data.contentType() == null ? "image/jpeg" : data.contentType();
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .cacheControl(CacheControl.maxAge(7, TimeUnit.DAYS).cachePublic())
                .body(data.data());
    }

    @PostMapping("/logout")
    public Result<Void> logout() {
        return Result.ok();
    }
}

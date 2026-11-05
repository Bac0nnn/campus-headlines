package com.campus.headlines.controller;

import com.campus.headlines.common.Result;
import com.campus.headlines.dto.LoginVO;
import com.campus.headlines.dto.MediaLoginRequest;
import com.campus.headlines.dto.ProfileUpdateRequest;
import com.campus.headlines.service.AuthService;
import com.campus.headlines.utils.UserContext;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import javax.validation.Valid;

@RestController
@RequestMapping("/api/media/auth")
@RequiredArgsConstructor
public class MediaAuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody MediaLoginRequest request) {
        return Result.ok(authService.loginMedia(request));
    }

    @GetMapping("/me")
    public Result<LoginVO> me() {
        return Result.ok(authService.me(UserContext.userId()));
    }

    /** 创作端修改个人资料，作者/审核员共用 ap_user */
    @PutMapping("/profile")
    public Result<LoginVO> updateProfile(@Valid @RequestBody ProfileUpdateRequest request) {
        return Result.ok(authService.updateProfile(UserContext.userId(), request));
    }

    /** 创作端上传头像，二进制写入 ap_user.avatar_data */
    @PostMapping("/avatar")
    public Result<LoginVO> uploadAvatar(@RequestParam("file") MultipartFile file) {
        return Result.ok(authService.uploadAvatar(UserContext.userId(), file));
    }
}

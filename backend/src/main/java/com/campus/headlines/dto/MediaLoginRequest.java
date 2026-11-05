package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class MediaLoginRequest {

    @NotBlank(message = "请输入用户名")
    private String username;

    @NotBlank(message = "请输入密码")
    private String password;
}

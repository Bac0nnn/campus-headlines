package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;

@Data
public class PhoneLoginRequest {

    @NotBlank(message = "请输入手机号")
    @Pattern(regexp = "^1\\d{10}$", message = "手机号格式不正确")
    private String phone;

    @NotBlank(message = "请输入验证码")
    private String code;
}

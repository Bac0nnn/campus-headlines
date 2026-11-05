package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;

@Data
public class RegisterRequest {

    @NotBlank(message = "请输入手机号")
    @Pattern(regexp = "^1\\d{10}$", message = "手机号格式不正确")
    private String phone;

    @NotBlank(message = "请输入昵称")
    @Size(min = 2, max = 20, message = "昵称长度需在 2-20 个字符之间")
    private String nickname;

    @NotBlank(message = "请输入密码")
    @Size(min = 6, max = 20, message = "密码长度需在 6-20 个字符之间")
    private String password;

    @NotBlank(message = "请再次输入密码")
    private String confirmPassword;

    /** 0 普通用户，1 作者，2 审核员 */
    @NotNull(message = "请选择账号类型")
    @Min(value = 0, message = "账号类型不正确")
    @Max(value = 2, message = "账号类型不正确")
    private Integer role;
}

package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

@Data
public class ProfileUpdateRequest {

    @NotBlank(message = "昵称不能为空")
    @Size(min = 2, max = 20, message = "昵称长度需在 2-20 个字符之间")
    private String nickname;

    @Size(max = 200, message = "个人简介不能超过 200 个字符")
    private String bio;

    /** 0 未知 / 1 男 / 2 女 */
    private Integer gender;

    private String avatar;
}

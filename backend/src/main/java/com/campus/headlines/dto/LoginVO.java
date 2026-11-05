package com.campus.headlines.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LoginVO {

    private String token;
    private Long id;
    private String name;
    private String avatar;
    /** USER / MEDIA，仅用于前端区分入口 */
    private String role;
    /** 0 普通用户，1 作者，2 审核员 */
    private Integer userRole;
    /** 作者/审核员关联的 wm_user.id */
    private Long wmUserId;
    /** 自媒体账号角色：0 作者，1 审核员 */
    private Integer accountRole;
    private String account;
    private String bio;
    private Integer gender;
}

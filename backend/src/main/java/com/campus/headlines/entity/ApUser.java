package com.campus.headlines.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("ap_user")
public class ApUser {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String phone;
    @JsonIgnore
    private String password;
    private String nickname;
    /** 0 普通用户，1 作者，2 审核员 */
    private Integer role;
    private String avatar;
    @JsonIgnore
    private byte[] avatarData;
    private String avatarType;
    private String bio;
    private Integer gender;
    private Integer status;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;
}

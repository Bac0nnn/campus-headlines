package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import java.util.List;

@Data
public class NewsSaveRequest {

    private Long id;

    @NotBlank(message = "请输入标题")
    @Size(max = 30, message = "标题不能超过 30 个字")
    private String title;

    @NotBlank(message = "请输入正文")
    private String content;

    @NotNull(message = "请选择频道")
    private Integer channelId;

    private List<String> labels;

    private Integer coverType;

    private List<String> coverImages;

    private Boolean submit;
}

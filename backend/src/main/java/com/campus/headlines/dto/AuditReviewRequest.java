package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.NotNull;

@Data
public class AuditReviewRequest {

    @NotNull(message = "请选择审核结果")
    private Boolean pass;

    private String reason;
}

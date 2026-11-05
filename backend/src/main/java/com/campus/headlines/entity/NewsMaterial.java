package com.campus.headlines.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("news_material")
public class NewsMaterial {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long newsId;
    private Long materialId;
    private Integer sort;
}

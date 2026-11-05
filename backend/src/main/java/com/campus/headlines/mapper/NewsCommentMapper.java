package com.campus.headlines.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.campus.headlines.entity.NewsComment;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface NewsCommentMapper extends BaseMapper<NewsComment> {
}

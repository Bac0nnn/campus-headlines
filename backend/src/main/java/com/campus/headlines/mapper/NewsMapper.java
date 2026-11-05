package com.campus.headlines.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.headlines.dto.NewsQuery;
import com.campus.headlines.entity.News;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface NewsMapper extends BaseMapper<News> {

    /**
     * 自媒体内容列表 / 审核列表：演示 MyBatis XML 动态 SQL（where、if、choose）。
     */
    Page<News> selectMediaNews(Page<News> page, @Param("q") NewsQuery query);

    /**
     * 各频道已发布文章数：演示 MyBatis foreach 标签。
     */
    List<Map<String, Object>> countByChannelIds(@Param("ids") List<Integer> ids);
}

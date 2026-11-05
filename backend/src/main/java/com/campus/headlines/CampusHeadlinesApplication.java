package com.campus.headlines;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@MapperScan("com.campus.headlines.mapper")
@SpringBootApplication
public class CampusHeadlinesApplication {

    public static void main(String[] args) {
        SpringApplication.run(CampusHeadlinesApplication.class, args);
    }
}

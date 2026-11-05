-- 校园头条数据库结构（MySQL 8.0，SSM）
CREATE DATABASE IF NOT EXISTS campus_headlines DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE campus_headlines;

-- 用户端用户：普通用户 / 作者 / 审核员统一账号
CREATE TABLE IF NOT EXISTS ap_user (
  id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  phone       VARCHAR(11)  NOT NULL COMMENT '手机号（登录名）',
  password    VARCHAR(100) DEFAULT NULL COMMENT 'BCrypt 密码',
  nickname    VARCHAR(32)  NOT NULL COMMENT '昵称',
  role        TINYINT      NOT NULL DEFAULT 0 COMMENT '0普通用户 1作者 2审核员',
  avatar      VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
  avatar_data LONGBLOB     DEFAULT NULL COMMENT '上传的头像二进制',
  avatar_type VARCHAR(50)  DEFAULT NULL COMMENT '头像 MIME 类型',
  bio         VARCHAR(200) DEFAULT NULL COMMENT '个人简介',
  gender      TINYINT      NOT NULL DEFAULT 0 COMMENT '0未知 1男 2女',
  status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0禁用',
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='统一用户表（普通用户/作者/审核员）';

-- 自媒体账号：作者与审核员在 wm_user 中的业务身份
CREATE TABLE IF NOT EXISTS wm_user (
  id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  ap_user_id  BIGINT       DEFAULT NULL COMMENT '关联 ap_user.id',
  username    VARCHAR(32)  NOT NULL COMMENT '登录名',
  password    VARCHAR(100) NOT NULL COMMENT 'BCrypt 密码',
  name        VARCHAR(32)  NOT NULL COMMENT '媒体号名称',
  avatar      VARCHAR(255) DEFAULT NULL COMMENT '头像',
  intro       VARCHAR(255) DEFAULT NULL COMMENT '简介',
  role        TINYINT      NOT NULL DEFAULT 0 COMMENT '0作者 1审核员',
  status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0禁用',
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  UNIQUE KEY uk_ap_user (ap_user_id),
  CONSTRAINT fk_wm_ap_user FOREIGN KEY (ap_user_id) REFERENCES ap_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自媒体账号';

-- 频道
CREATE TABLE IF NOT EXISTS channel (
  id          INT          NOT NULL AUTO_INCREMENT COMMENT '主键',
  name        VARCHAR(32)  NOT NULL COMMENT '频道名称',
  description VARCHAR(255) DEFAULT NULL COMMENT '描述',
  sort        INT          NOT NULL DEFAULT 0 COMMENT '排序',
  status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1启用 0停用',
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='频道';

-- 素材：图片二进制直接保存在数据库中
CREATE TABLE IF NOT EXISTS material (
  id           BIGINT       NOT NULL AUTO_INCREMENT,
  wm_user_id   BIGINT       NOT NULL COMMENT '所属作者',
  url          VARCHAR(255) NOT NULL COMMENT '访问地址',
  type         TINYINT      NOT NULL DEFAULT 0 COMMENT '0图片 1视频',
  size         BIGINT       NOT NULL DEFAULT 0 COMMENT '字节',
  width        INT          DEFAULT NULL,
  height       INT          DEFAULT NULL,
  content_type VARCHAR(50)  DEFAULT NULL COMMENT 'MIME 类型',
  original_name VARCHAR(255) DEFAULT NULL COMMENT '原始文件名',
  data         LONGBLOB     DEFAULT NULL COMMENT '图片二进制',
  is_collected TINYINT      NOT NULL DEFAULT 0 COMMENT '0未收藏 1已收藏',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_wm_collect (wm_user_id, is_collected),
  CONSTRAINT fk_material_wm FOREIGN KEY (wm_user_id) REFERENCES wm_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材（图片入库）';

-- 文章
CREATE TABLE IF NOT EXISTS news (
  id           BIGINT       NOT NULL AUTO_INCREMENT,
  wm_user_id   BIGINT       NOT NULL COMMENT '作者',
  channel_id   INT          NOT NULL COMMENT '频道',
  title        VARCHAR(60)  NOT NULL COMMENT '标题',
  content      LONGTEXT     NOT NULL COMMENT '正文 HTML',
  cover_type   TINYINT      NOT NULL DEFAULT 0 COMMENT '0无图 1单图 3三图',
  cover_images VARCHAR(1000) DEFAULT NULL COMMENT '封面地址，逗号分隔（指向素材图片接口）',
  labels       VARCHAR(200) DEFAULT NULL COMMENT '标签，逗号分隔',
  status       TINYINT      NOT NULL DEFAULT 0 COMMENT '0草稿 1待审核 2通过 3驳回',
  is_top       TINYINT      NOT NULL DEFAULT 0 COMMENT '是否置顶',
  publish_time DATETIME     DEFAULT NULL,
  views        INT          NOT NULL DEFAULT 0,
  likes        INT          NOT NULL DEFAULT 0,
  comments     INT          NOT NULL DEFAULT 0,
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_channel_status_time (channel_id, status, publish_time),
  KEY idx_wm_status (wm_user_id, status),
  CONSTRAINT fk_news_wm FOREIGN KEY (wm_user_id) REFERENCES wm_user (id),
  CONSTRAINT fk_news_channel FOREIGN KEY (channel_id) REFERENCES channel (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章';

-- 文章素材关联
CREATE TABLE IF NOT EXISTS news_material (
  id          BIGINT NOT NULL AUTO_INCREMENT,
  news_id     BIGINT NOT NULL,
  material_id BIGINT NOT NULL,
  sort        INT    NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_news_material (news_id, material_id),
  CONSTRAINT fk_nm_news FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE,
  CONSTRAINT fk_nm_material FOREIGN KEY (material_id) REFERENCES material (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章素材关联';

-- 点赞
CREATE TABLE IF NOT EXISTS news_like (
  id          BIGINT   NOT NULL AUTO_INCREMENT,
  news_id     BIGINT   NOT NULL,
  user_id     BIGINT   NOT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_news_user (news_id, user_id),
  CONSTRAINT fk_like_news FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE,
  CONSTRAINT fk_like_user FOREIGN KEY (user_id) REFERENCES ap_user (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章点赞';

-- 评论
CREATE TABLE IF NOT EXISTS news_comment (
  id          BIGINT       NOT NULL AUTO_INCREMENT,
  news_id     BIGINT       NOT NULL,
  user_id     BIGINT       NOT NULL,
  content     VARCHAR(500) NOT NULL,
  status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0隐藏',
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_news_time (news_id, create_time),
  CONSTRAINT fk_comment_news FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE,
  CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES ap_user (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章评论';

-- 审核记录
CREATE TABLE IF NOT EXISTS audit_record (
  id          BIGINT       NOT NULL AUTO_INCREMENT,
  news_id     BIGINT       NOT NULL,
  auditor_id  BIGINT       NOT NULL COMMENT '审核员 wm_user.id',
  result      TINYINT      NOT NULL COMMENT '1通过 2驳回',
  reason      VARCHAR(255) DEFAULT NULL COMMENT '审核意见',
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_audit_news (news_id),
  CONSTRAINT fk_audit_news FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE,
  CONSTRAINT fk_audit_user FOREIGN KEY (auditor_id) REFERENCES wm_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审核记录';

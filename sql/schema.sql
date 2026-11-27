-- 校园二手书交易平台 数据库结构（MySQL 8.0）
-- 使用方式：mysql -u root -p < sql/schema.sql
-- 说明：应用层通过 SQLAlchemy 建模，本文件用于数据库部署、评审与文档留档。

CREATE DATABASE IF NOT EXISTS `campus_books`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `campus_books`;

-- 用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` VARCHAR(40) NOT NULL COMMENT '登录用户名',
  `nickname` VARCHAR(40) NOT NULL COMMENT '昵称',
  `student_id` VARCHAR(20) DEFAULT NULL COMMENT '学号，唯一',
  `campus` VARCHAR(40) DEFAULT NULL COMMENT '所在校区',
  `contact` VARCHAR(60) DEFAULT NULL COMMENT '联系方式',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希（werkzeug 生成）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_student_id` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 图书表
CREATE TABLE IF NOT EXISTS `books` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title` VARCHAR(100) NOT NULL COMMENT '书名',
  `author` VARCHAR(60) DEFAULT NULL COMMENT '作者',
  `category` VARCHAR(20) NOT NULL COMMENT '分类',
  `condition` VARCHAR(20) NOT NULL COMMENT '成色',
  `price` DECIMAL(8,2) NOT NULL COMMENT '售价',
  `original_price` DECIMAL(8,2) DEFAULT NULL COMMENT '原价',
  `description` TEXT COMMENT '图书描述',
  `cover` VARCHAR(200) DEFAULT NULL COMMENT '封面图文件名',
  `status` VARCHAR(20) NOT NULL DEFAULT 'on_sale' COMMENT '状态：on_sale/reserved/sold/off_shelf',
  `views` INT DEFAULT 0 COMMENT '浏览量',
  `seller_id` INT NOT NULL COMMENT '卖家用户 id',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  PRIMARY KEY (`id`),
  KEY `idx_seller` (`seller_id`),
  KEY `idx_status` (`status`),
  KEY `idx_category` (`category`),
  KEY `idx_title` (`title`),
  CONSTRAINT `fk_book_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书表';

-- 收藏表
CREATE TABLE IF NOT EXISTS `favorites` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` INT NOT NULL COMMENT '收藏用户 id',
  `book_id` INT NOT NULL COMMENT '被收藏图书 id',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_favorite_user_book` (`user_id`, `book_id`),
  KEY `idx_favorite_user` (`user_id`),
  KEY `idx_favorite_book` (`book_id`),
  CONSTRAINT `fk_favorite_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_favorite_book` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 订单表
CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `order_no` VARCHAR(32) NOT NULL COMMENT '订单号',
  `book_id` INT NOT NULL COMMENT '图书 id',
  `buyer_id` INT NOT NULL COMMENT '买家 id',
  `seller_id` INT NOT NULL COMMENT '卖家 id',
  `amount` DECIMAL(8,2) NOT NULL COMMENT '成交金额',
  `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态：pending/completed/cancelled',
  `remark` VARCHAR(200) DEFAULT NULL COMMENT '买家留言',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_book` (`book_id`),
  KEY `idx_buyer` (`buyer_id`),
  KEY `idx_seller` (`seller_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_order_book` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`),
  CONSTRAINT `fk_order_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_order_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

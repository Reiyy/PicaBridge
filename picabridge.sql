-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2025-03-13 02:27:24
-- 服务器版本： 10.6.4-MariaDB-log
-- PHP 版本： 7.4.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `picabridge`
--

-- --------------------------------------------------------

--
-- 表的结构 `comic_info`
--

CREATE TABLE `comic_info` (
  `id` varchar(255) NOT NULL,
  `creator` varchar(255) DEFAULT '7v5za3f62102s6t81wue5uyo',
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT 'PicBridge - 哔咔桥',
  `author` varchar(255) DEFAULT NULL,
  `chineseTeam` varchar(255) DEFAULT NULL,
  `categories` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '[]',
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '[]',
  `pagesCount` int(11) DEFAULT NULL,
  `epsCount` int(11) DEFAULT 1,
  `finished` tinyint(1) DEFAULT 1,
  `updated_at` int(10) DEFAULT 0,
  `created_at` int(10) DEFAULT 0,
  `allowDownload` tinyint(1) DEFAULT 0,
  `allowComment` tinyint(1) DEFAULT 0,
  `viewsCount` int(11) DEFAULT 0,
  `likesCount` int(11) DEFAULT 0,
  `commentsCount` int(11) DEFAULT 0,
  `viewed_at` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '[]' CHECK (json_valid(`viewed_at`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `comic_info`
--

INSERT INTO `comic_info` (`id`, `creator`, `title`, `description`, `author`, `chineseTeam`, `categories`, `tags`, `pagesCount`, `epsCount`, `finished`, `updated_at`, `created_at`, `allowDownload`, `allowComment`, `viewsCount`, `likesCount`, `commentsCount`, `viewed_at`) VALUES
('5822a6e3ad7ede654696e482', '7v5za3f62102s6t81wue5uyo', '留言板', '留言板', '未知', '未知', '[]', '[]', 1, 1, 1, 1633072800, 1633072800, 0, 1, 0, 0, 1, '[]');

-- --------------------------------------------------------

--
-- 表的结构 `comments`
--

CREATE TABLE `comments` (
  `id` varchar(255) NOT NULL,
  `comic_id` varchar(255) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `parent_id` varchar(255) DEFAULT NULL,
  `created_at` int(10) NOT NULL DEFAULT 0,
  `likesCount` int(10) DEFAULT 0,
  `commentsCount` int(10) NOT NULL,
  `isTop` tinyint(1) NOT NULL,
  `hide` tinyint(1) NOT NULL,
  `hideTop` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `comments`
--

INSERT INTO `comments` (`id`, `comic_id`, `user_id`, `content`, `parent_id`, `created_at`, `likesCount`, `commentsCount`, `isTop`, `hide`, `hideTop`) VALUES
('i9oht7m7avd9j269aomxkvsw', '5822a6e3ad7ede654696e482', '7v5za3f62102s6t81wue5uyo', '留言板规则:\n1.没什么规则=v=', NULL, 1730048893, 1, 0, 1, 0, 1),
('twuyvxh30brpsnrs9225jlpx', '5822a6e3ad7ede654696e482', '7v5za3f62102s6t81wue5uyo', '欢迎来到哔咔桥PicaBridge!=v=', NULL, 1730045031, 1, 0, 1, 0, 0);

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` varchar(24) NOT NULL,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `birthday` date NOT NULL,
  `gender` enum('m','f','bot') NOT NULL,
  `question1` varchar(255) DEFAULT NULL,
  `answer1` varchar(255) DEFAULT NULL,
  `question2` varchar(255) DEFAULT NULL,
  `answer2` varchar(255) DEFAULT NULL,
  `question3` varchar(255) DEFAULT NULL,
  `answer3` varchar(255) DEFAULT NULL,
  `createdate` timestamp NULL DEFAULT current_timestamp(),
  `title` varchar(255) DEFAULT '萌新',
  `description` text DEFAULT '还没有写哦~',
  `exp` int(11) DEFAULT 0,
  `level` int(11) DEFAULT 1,
  `role` varchar(255) DEFAULT '',
  `avatar` varchar(255) DEFAULT '',
  `frame` varchar(255) DEFAULT '',
  `verified` tinyint(1) DEFAULT 0,
  `characters` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '[]' CHECK (json_valid(`characters`)),
  `favourite` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '{}' CHECK (json_valid(`favourite`)),
  `like` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '[]',
  `isPunched` int(10) DEFAULT 0,
  `likeComments` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '[]',
  `mode` char(20) DEFAULT 'sfw'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `email`, `name`, `password`, `birthday`, `gender`, `question1`, `answer1`, `question2`, `answer2`, `question3`, `answer3`, `createdate`, `title`, `description`, `exp`, `level`, `role`, `avatar`, `frame`, `verified`, `characters`, `favourite`, `like`, `isPunched`, `likeComments`, `mode`) VALUES
('7v5za3f62102s6t81wue5uyo', 'Picabridge', '哔咔桥PicaBridge', '$2b$12$9k4Fs7cT.A9nk/B74pgTHeSW4ZYBiuzVmp/ufUuE13uMk3Sww2Gva', '2000-01-01', 'm', '1', '1', '2', '2', '3', '3', '2024-09-30 19:13:08', '管理员', '', 54056180, 233, 'knight', '', NULL, 0, '[\"knight\", \"official\"]', '{}', '[]', 1741731099, '[]', 'nsfw');

--
-- 转储表的索引
--

--
-- 表的索引 `comic_info`
--
ALTER TABLE `comic_info`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `name` (`name`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

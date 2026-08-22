CREATE TABLE f_8e00a8e9__users (
  id CHAR(36) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_f_8e00a8e9_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE f_8e00a8e9__subjects (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_subjects_user FOREIGN KEY (user_id) REFERENCES f_8e00a8e9__users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE f_8e00a8e9__tasks (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  subject_id CHAR(36) NOT NULL,
  title VARCHAR(255) NOT NULL,
  due_date DATE NOT NULL,
  priority ENUM('low','medium','high') NOT NULL,
  status ENUM('to_do','in_progress','done') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES f_8e00a8e9__users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_tasks_subject FOREIGN KEY (subject_id) REFERENCES f_8e00a8e9__subjects(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE f_8e006bb8__user_viewport_preferences (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  device_category VARCHAR(20) NOT NULL,
  layout_mode VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT chk_device_category_user_viewport CHECK (device_category IN ('desktop','tablet','mobile')),
  CONSTRAINT chk_layout_mode_user_viewport CHECK (layout_mode IN ('side_by_side','horizontal_scroll','vertical_stack','tabs'))
) ENGINE=InnoDB;

CREATE TABLE f_8e006bb8__touch_target_configurations (
  id CHAR(36) NOT NULL,
  element_type VARCHAR(50) NOT NULL,
  minimum_width_px INT NOT NULL,
  minimum_height_px INT NOT NULL,
  minimum_spacing_px INT NOT NULL,
  device_category VARCHAR(20) NOT NULL,
  is_active BOOLEAN NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT chk_element_type_touch_target CHECK (element_type IN ('button','drag_handle','form_field','card','column_header')),
  CONSTRAINT chk_minimum_width_px CHECK (minimum_width_px BETWEEN 44 AND 200),
  CONSTRAINT chk_minimum_height_px CHECK (minimum_height_px BETWEEN 44 AND 200),
  CONSTRAINT chk_minimum_spacing_px CHECK (minimum_spacing_px BETWEEN 8 AND 48),
  CONSTRAINT chk_device_category_touch_target CHECK (device_category IN ('desktop','tablet','mobile'))
) ENGINE=InnoDB;


CREATE TABLE f_b7688c8b__users (
  id CHAR(36) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE f_b7688c8b__sessions (
  id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  token VARCHAR(255) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES f_b7688c8b__users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE `f_384935a0__homework_cards` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `subject_id` CHAR(36) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `due_date` DATE NOT NULL,
  `priority` ENUM('High','Medium','Low') NOT NULL,
  `description` LONGTEXT,
  `status` ENUM('to_do','in_progress','done') NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE f_40702744__accounts (
  id CHAR(36) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_8df07551__users` (
  `id` CHAR(36) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE `f_8df07551__subjects` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_subjects_user` FOREIGN KEY (`user_id`) REFERENCES `f_8df07551__users`(`id`)
) ENGINE=InnoDB;

CREATE TABLE `f_8df07551__tasks` (
  `id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `subject_id` CHAR(36) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `due_date` DATE NOT NULL,
  `priority` ENUM('low','medium','high') NOT NULL,
  `status` ENUM('todo','in_progress','done') NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_tasks_user` FOREIGN KEY (`user_id`) REFERENCES `f_8df07551__users`(`id`),
  CONSTRAINT `fk_tasks_subject` FOREIGN KEY (`subject_id`) REFERENCES `f_8df07551__subjects`(`id`)
) ENGINE=InnoDB;


CREATE TABLE `f_7897884e__homework_card_status` (
  `id` CHAR(36) NOT NULL,
  `homework_card_id` CHAR(36) NOT NULL,
  `column_name` ENUM('to_do','in_progress','done') NOT NULL,
  `position` INT NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CHECK (`position` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_c90dae67__subjects` (
  `id` CHAR(36) NOT NULL,
  `student_id` CHAR(36) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_ea5acd92__user_credentials` (
  `user_id` CHAR(36) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- No database tables are required for feature: capability_visual_urgency_indicators_79524665


CREATE TABLE `f_a0308110__homework_card_status` (
  `id` CHAR(36) NOT NULL,
  `homework_card_id` CHAR(36) NOT NULL,
  `column_status` ENUM('to_do','in_progress','done') NOT NULL,
  `position_in_column` INT UNSIGNED NOT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

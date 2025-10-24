-- 创建用户模型偏好设置表
CREATE TABLE user_model_preference (
  id bigint NOT NULL AUTO_INCREMENT COMMENT 'ID',
  user_id bigint NOT NULL COMMENT '用户ID',
  model_type varchar(50) NOT NULL COMMENT '模型类型(ASR/LLM/TTS/VAD/Memory等)',
  model_config_id varchar(50) NOT NULL COMMENT '默认模型配置ID',
  creator bigint COMMENT '创建者',
  create_date datetime COMMENT '创建时间',
  updater bigint COMMENT '更新者',
  update_date datetime COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_model_type (user_id, model_type),
  KEY idx_user_id (user_id),
  KEY idx_model_type (model_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户模型偏好设置';


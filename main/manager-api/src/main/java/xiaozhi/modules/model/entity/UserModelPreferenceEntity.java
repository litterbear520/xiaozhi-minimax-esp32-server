package xiaozhi.modules.model.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;
import xiaozhi.common.entity.BaseEntity;

/**
 * 用户模型偏好设置
 *
 * @author system
 */
@Data
@EqualsAndHashCode(callSuper=false)
@TableName("user_model_preference")
public class UserModelPreferenceEntity extends BaseEntity {
	private static final long serialVersionUID = 1L;

	/**
	 * 用户ID
	 */
	private Long userId;
	/**
	 * 模型类型(ASR/LLM/TTS/VAD/Memory等)
	 */
	private String modelType;
	/**
	 * 默认模型配置ID
	 */
	private String modelConfigId;

}


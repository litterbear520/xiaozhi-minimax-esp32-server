package xiaozhi.modules.model.service;

/**
 * 用户模型偏好设置
 *
 * @author system
 */
public interface UserModelPreferenceService {

    /**
     * 获取用户指定模型类型的默认配置ID
     *
     * @param userId 用户ID
     * @param modelType 模型类型
     * @return 模型配置ID
     */
    String getUserDefaultModelId(Long userId, String modelType);

    /**
     * 设置用户指定模型类型的默认配置
     *
     * @param userId 用户ID
     * @param modelType 模型类型
     * @param modelConfigId 模型配置ID
     */
    void setUserDefaultModel(Long userId, String modelType, String modelConfigId);

    /**
     * 删除用户某个模型类型的偏好设置
     *
     * @param userId 用户ID
     * @param modelType 模型类型
     */
    void deleteUserPreference(Long userId, String modelType);
}


package xiaozhi.modules.model.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import xiaozhi.modules.model.dao.UserModelPreferenceDao;
import xiaozhi.modules.model.entity.UserModelPreferenceEntity;
import xiaozhi.modules.model.service.UserModelPreferenceService;
import xiaozhi.modules.security.user.SecurityUser;

/**
 * 用户模型偏好设置
 *
 * @author system
 */
@Service
@AllArgsConstructor
public class UserModelPreferenceServiceImpl implements UserModelPreferenceService {

    private final UserModelPreferenceDao baseDao;

    @Override
    public String getUserDefaultModelId(Long userId, String modelType) {
        QueryWrapper<UserModelPreferenceEntity> wrapper = new QueryWrapper<>();
        wrapper.eq("user_id", userId);
        wrapper.eq("model_type", modelType);
        
        UserModelPreferenceEntity preference = baseDao.selectOne(wrapper);
        return preference != null ? preference.getModelConfigId() : null;
    }

    @Override
    public void setUserDefaultModel(Long userId, String modelType, String modelConfigId) {
        QueryWrapper<UserModelPreferenceEntity> wrapper = new QueryWrapper<>();
        wrapper.eq("user_id", userId);
        wrapper.eq("model_type", modelType);
        
        UserModelPreferenceEntity preference = baseDao.selectOne(wrapper);
        
        if (preference == null) {
            // 新增
            preference = new UserModelPreferenceEntity();
            preference.setUserId(userId);
            preference.setModelType(modelType);
            preference.setModelConfigId(modelConfigId);
            preference.setCreator(SecurityUser.getUserId());
            baseDao.insert(preference);
        } else {
            // 更新
            preference.setModelConfigId(modelConfigId);
            baseDao.updateById(preference);
        }
    }

    @Override
    public void deleteUserPreference(Long userId, String modelType) {
        QueryWrapper<UserModelPreferenceEntity> wrapper = new QueryWrapper<>();
        wrapper.eq("user_id", userId);
        wrapper.eq("model_type", modelType);
        baseDao.delete(wrapper);
    }
}


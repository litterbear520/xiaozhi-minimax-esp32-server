package xiaozhi.modules.model.dao;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.common.dao.BaseDao;
import xiaozhi.modules.model.entity.UserModelPreferenceEntity;

/**
 * 用户模型偏好设置
 *
 * @author system
 */
@Mapper
public interface UserModelPreferenceDao extends BaseDao<UserModelPreferenceEntity> {
	
}


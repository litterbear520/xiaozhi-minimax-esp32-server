package xiaozhi.modules.sys.service.impl;

import cn.hutool.json.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import xiaozhi.modules.model.dao.ModelConfigDao;
import xiaozhi.modules.model.entity.ModelConfigEntity;
import xiaozhi.modules.sys.service.UserInitService;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * 用户初始化服务实现
 *
 * @author system
 */
@Service
@AllArgsConstructor
@Slf4j
public class UserInitServiceImpl implements UserInitService {

    private final ModelConfigDao modelConfigDao;
    
    // 需要清空的敏感字段列表
    private static final List<String> SENSITIVE_FIELDS = Arrays.asList(
        "api_key", "apiKey", "apikey", 
        "access_token", "accessToken", "access_key", "accessKey",
        "secret_key", "secretKey", "secret",
        "password", "passwd", "pwd",
        "token", "appid", "app_id", "group_id", "groupId"
    );

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void initUserModelConfigs(Long userId) {
        log.info("开始为用户 {} 初始化默认模型配置", userId);
        
        // 查找admin用户（userId=1）的所有配置作为模板
        QueryWrapper<ModelConfigEntity> wrapper = new QueryWrapper<>();
        wrapper.eq("creator", 1L); // admin用户ID为1
        wrapper.orderByAsc("sort");
        
        List<ModelConfigEntity> templateConfigs = modelConfigDao.selectList(wrapper);
        
        if (templateConfigs == null || templateConfigs.isEmpty()) {
            log.warn("未找到admin用户的模板配置，跳过用户 {} 的配置初始化", userId);
            return;
        }
        
        log.info("找到 {} 个模板配置，开始复制", templateConfigs.size());
        
        List<ModelConfigEntity> newConfigs = new ArrayList<>();
        for (ModelConfigEntity template : templateConfigs) {
            ModelConfigEntity newConfig = new ModelConfigEntity();
            
            // 复制基本信息
            newConfig.setModelType(template.getModelType());
            newConfig.setModelCode(template.getModelCode());
            newConfig.setModelName(template.getModelName());
            newConfig.setIsEnabled(template.getIsEnabled());
            newConfig.setSort(template.getSort());
            
            // 复制配置JSON并清空敏感信息
            JSONObject cleanedConfigJson = clearSensitiveFields(template.getConfigJson());
            newConfig.setConfigJson(cleanedConfigJson);
            
            // 设置创建者为新用户
            newConfig.setCreator(userId);
            
            newConfigs.add(newConfig);
        }
        
        // 批量插入
        for (ModelConfigEntity config : newConfigs) {
            modelConfigDao.insert(config);
        }
        
        log.info("成功为用户 {} 复制了 {} 个配置", userId, newConfigs.size());
    }
    
    /**
     * 清空配置JSON中的敏感字段
     */
    private JSONObject clearSensitiveFields(JSONObject configJson) {
        if (configJson == null || configJson.isEmpty()) {
            return new JSONObject();
        }
        
        try {
            // 创建副本
            JSONObject cleaned = new JSONObject(configJson);
            
            // 遍历并清空敏感字段
            for (String field : SENSITIVE_FIELDS) {
                if (cleaned.containsKey(field)) {
                    cleaned.set(field, "");
                    log.debug("清空敏感字段: {}", field);
                }
            }
            
            return cleaned;
        } catch (Exception e) {
            log.error("清空敏感字段失败，返回空JSON", e);
            return new JSONObject();
        }
    }
}


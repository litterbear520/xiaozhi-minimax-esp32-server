package xiaozhi.modules.model.controller;

import java.util.List;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import xiaozhi.common.page.PageData;
import xiaozhi.common.utils.ConvertUtils;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.agent.service.AgentTemplateService;
import xiaozhi.modules.config.service.ConfigService;
import xiaozhi.modules.model.dto.*;
import xiaozhi.modules.model.entity.ModelConfigEntity;
import xiaozhi.modules.model.service.ModelConfigService;
import xiaozhi.modules.model.service.ModelProviderService;
import xiaozhi.modules.model.service.UserModelPreferenceService;
import xiaozhi.modules.security.user.SecurityUser;
import xiaozhi.modules.timbre.service.TimbreService;

@AllArgsConstructor
@RestController
@RequestMapping("/models")
@Tag(name = "模型配置")
public class ModelController {

    private final ModelProviderService modelProviderService;
    private final TimbreService timbreService;
    private final ModelConfigService modelConfigService;
    private final ConfigService configService;
    private final AgentTemplateService agentTemplateService;
    private final UserModelPreferenceService userModelPreferenceService;

    @GetMapping("/names")
    @Operation(summary = "获取所有模型名称")
    @RequiresPermissions("sys:role:normal")
    public Result<List<ModelBasicInfoDTO>> getModelNames(@RequestParam String modelType,
            @RequestParam(required = false) String modelName) {
        List<ModelBasicInfoDTO> modelList = modelConfigService.getModelCodeList(modelType, modelName);
        return new Result<List<ModelBasicInfoDTO>>().ok(modelList);
    }

    @GetMapping("/llm/names")
    @Operation(summary = "获取LLM模型信息")
    @RequiresPermissions("sys:role:normal")
    public Result<List<LlmModelBasicInfoDTO>> getLlmModelCodeList(@RequestParam(required = false) String modelName) {
        List<LlmModelBasicInfoDTO> llmModelCodeList = modelConfigService.getLlmModelCodeList(modelName);
        return new Result<List<LlmModelBasicInfoDTO>>().ok(llmModelCodeList);
    }

    @GetMapping("/{modelType}/provideTypes")
    @Operation(summary = "获取模型供应器列表")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限，所有用户都需要查看提供商列表
    public Result<List<ModelProviderDTO>> getModelProviderList(@PathVariable String modelType) {
        List<ModelProviderDTO> modelProviderDTOS = modelProviderService.getListByModelType(modelType);
        return new Result<List<ModelProviderDTO>>().ok(modelProviderDTOS);
    }

    @GetMapping("/list")
    @Operation(summary = "获取模型配置列表")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限，所有用户可访问
    public Result<PageData<ModelConfigDTO>> getModelConfigList(
            @RequestParam(required = true) String modelType,
            @RequestParam(required = false) String modelName,
            @RequestParam(required = true, defaultValue = "0") String page,
            @RequestParam(required = true, defaultValue = "10") String limit) {
        // Service层会根据用户身份自动过滤数据
        PageData<ModelConfigDTO> pageList = modelConfigService.getPageList(modelType, modelName, page, limit);
        return new Result<PageData<ModelConfigDTO>>().ok(pageList);
    }

    @PostMapping("/{modelType}/{provideCode}")
    @Operation(summary = "新增模型配置")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限，所有用户可创建自己的配置
    public Result<ModelConfigDTO> addModelConfig(@PathVariable String modelType,
            @PathVariable String provideCode,
            @RequestBody ModelConfigBodyDTO modelConfigBodyDTO) {
        // Service层会自动设置creator为当前用户
        ModelConfigDTO modelConfigDTO = modelConfigService.add(modelType, provideCode, modelConfigBodyDTO);
        configService.getConfig(false);
        return new Result<ModelConfigDTO>().ok(modelConfigDTO);
    }

    @PutMapping("/{modelType}/{provideCode}/{id}")
    @Operation(summary = "编辑模型配置")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限，用户可编辑自己的配置
    public Result<ModelConfigDTO> editModelConfig(@PathVariable String modelType,
            @PathVariable String provideCode,
            @PathVariable String id,
            @RequestBody ModelConfigBodyDTO modelConfigBodyDTO) {
        // Service层会校验权限：只能编辑自己的配置
        ModelConfigDTO modelConfigDTO = modelConfigService.edit(modelType, provideCode, id, modelConfigBodyDTO);
        configService.getConfig(false);
        return new Result<ModelConfigDTO>().ok(modelConfigDTO);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除模型配置")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限，用户可删除自己的配置
    public Result<Void> deleteModelConfig(@PathVariable String id) {
        // Service层会校验权限：只能删除自己的配置
        modelConfigService.delete(id);
        return new Result<>();
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取模型配置")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限
    public Result<ModelConfigDTO> getModelConfig(@PathVariable String id) {
        ModelConfigEntity item = modelConfigService.selectById(id);
        ModelConfigDTO modelConfigDTO = ConvertUtils.sourceToTarget(item, ModelConfigDTO.class);
        return new Result<ModelConfigDTO>().ok(modelConfigDTO);
    }

    @PutMapping("/enable/{id}/{status}")
    @Operation(summary = "启用/关闭模型配置")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限
    public Result<Void> enableModelConfig(@PathVariable String id, @PathVariable Integer status) {
        ModelConfigEntity entity = modelConfigService.selectById(id);
        if (entity == null) {
            return new Result<Void>().error("模型配置不存在");
        }
        entity.setIsEnabled(status);
        modelConfigService.updateById(entity);
        return new Result<Void>();
    }

    @PutMapping("/default/{id}")
    @Operation(summary = "设置默认模型")
    @RequiresPermissions("sys:role:normal")  // 改为normal权限，所有用户都可以设置默认模型
    public Result<Void> setDefaultModel(@PathVariable String id) {
        ModelConfigEntity entity = modelConfigService.selectById(id);
        if (entity == null) {
            return new Result<Void>().error("模型配置不存在");
        }
        
        // 使用用户级别的偏好设置，而不是全局设置
        Long currentUserId = SecurityUser.getUserId();
        userModelPreferenceService.setUserDefaultModel(currentUserId, entity.getModelType(), id);

        // 更新模板表中对应的模型ID（仅对当前用户生效）
        agentTemplateService.updateDefaultTemplateModelId(entity.getModelType(), entity.getId());

        // 刷新配置
        configService.getConfig(false);
        return new Result<Void>();
    }

    @GetMapping("/{modelId}/voices")
    @Operation(summary = "获取模型音色")
    @RequiresPermissions("sys:role:normal")
    public Result<List<VoiceDTO>> getVoiceList(@PathVariable String modelId,
            @RequestParam(required = false) String voiceName) {
        List<VoiceDTO> voiceList = timbreService.getVoiceNames(modelId, voiceName);
        return new Result<List<VoiceDTO>>().ok(voiceList);
    }
}

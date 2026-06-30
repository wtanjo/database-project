<template>
  <div>
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>爬虫参数配置</span>
          <el-button size="small" :icon="Refresh" @click="loadConfig">刷新</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="180px"
        style="max-width: 560px"
        v-loading="loading"
      >
        <el-form-item label="请求间隔 (秒)" prop="download_delay">
          <el-input-number
            v-model="form.download_delay"
            :min="0"
            :step="0.1"
            :precision="1"
            style="width: 100%"
          />
          <div class="form-tip">每次请求之间的等待时间，避免对目标服务器造成过大压力</div>
        </el-form-item>

        <el-form-item label="爬取深度" prop="depth_limit">
          <el-input-number
            v-model="form.depth_limit"
            :min="0"
            :max="20"
            :step="1"
            style="width: 100%"
          />
          <div class="form-tip">0 = 仅起始页，1 = 起始页 + 一级链接，2 = 起始页 + 两级链接</div>
        </el-form-item>

        <el-form-item label="单次最大页数" prop="closespider_pagecount">
          <el-input-number
            v-model="form.closespider_pagecount"
            :min="1"
            :step="1"
            style="width: 100%"
          />
          <div class="form-tip">单次任务最多爬取的页面数量，防止无限扩散</div>
        </el-form-item>

        <el-form-item label="日志级别" prop="log_level">
          <el-select v-model="form.log_level" style="width: 100%">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
            <el-option label="CRITICAL" value="CRITICAL" />
          </el-select>
          <div class="form-tip">控制爬虫运行时的日志输出详细程度</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getConfig, updateConfig } from '@/api/index'

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  download_delay: 1.0,
  depth_limit: 2,
  closespider_pagecount: 100,
  log_level: 'WARNING',
})

const rules: FormRules = {
  download_delay: [
    { required: true, message: '请输入请求间隔', trigger: 'blur' },
  ],
  depth_limit: [
    { required: true, message: '请输入爬取深度', trigger: 'blur' },
  ],
  closespider_pagecount: [
    { required: true, message: '请输入单次最大页数', trigger: 'blur' },
  ],
  log_level: [
    { required: true, message: '请选择日志级别', trigger: 'change' },
  ],
}

const defaultForm = { ...form }

async function loadConfig() {
  loading.value = true
  try {
    const res: any = await getConfig()
    if (res.code === 0) {
      form.download_delay = res.data.download_delay
      form.depth_limit = res.data.depth_limit
      form.closespider_pagecount = res.data.closespider_pagecount
      form.log_level = res.data.log_level
      Object.assign(defaultForm, { ...form })
    }
  } catch {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const res: any = await updateConfig({ ...form })
    if (res.code === 0) {
      ElMessage.success('配置保存成功')
      Object.assign(defaultForm, { ...form })
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '请求失败')
  } finally {
    saving.value = false
  }
}

function handleReset() {
  Object.assign(form, { ...defaultForm })
  formRef.value?.clearValidate()
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 4px;
}
</style>

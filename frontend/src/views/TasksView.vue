<template>
  <div>
    <!-- 提交任务 -->
    <el-card class="submit-card" shadow="never">
      <el-form inline @submit.prevent="handleSubmit">
        <el-form-item label="目标 URL">
          <el-input
            v-model="inputUrl"
            placeholder="https://quotes.toscrape.com/"
            style="width: 420px"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" native-type="submit">
            开始爬取
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 任务列表 -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-button size="small" :icon="Refresh" @click="fetchTasks">刷新</el-button>
        </div>
      </template>

      <el-table :data="tasks" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="target_url" label="目标 URL" show-overflow-tooltip min-width="260" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="page_count" label="页数" width="70" align="center" />
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="完成时间" width="180">
          <template #default="{ row }">{{ row.finished_at ? formatTime(row.finished_at) : '—' }}</template>
        </el-table-column>
        <el-table-column prop="error_msg" label="错误信息" show-overflow-tooltip min-width="160" />
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchTasks"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { createTask, getTasks } from '@/api/index'

const inputUrl = ref('')
const submitting = ref(false)
const loading = ref(false)
const tasks = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
let pollingTimer: ReturnType<typeof setInterval> | null = null

async function handleSubmit() {
  if (!inputUrl.value.trim()) {
    ElMessage.warning('请输入目标 URL')
    return
  }
  submitting.value = true
  try {
    const res: any = await createTask(inputUrl.value.trim())
    if (res.code === 0) {
      ElMessage.success(`任务已创建，ID: ${res.data.task_id}`)
      inputUrl.value = ''
      await fetchTasks()
    } else {
      ElMessage.error(res.message || '创建失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '请求失败')
  } finally {
    submitting.value = false
  }
}

async function fetchTasks() {
  loading.value = true
  try {
    const res: any = await getTasks(page.value, pageSize.value)
    if (res.code === 0) {
      tasks.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function statusType(status: string) {
  const map: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] ?? ''
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '排队中',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] ?? status
}

function formatTime(iso: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchTasks()
  // 每 5 秒轮询一次，刷新进行中的任务状态
  pollingTimer = setInterval(fetchTasks, 5000)
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})
</script>

<style scoped>
.submit-card :deep(.el-card__body) {
  padding: 16px 20px 8px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>

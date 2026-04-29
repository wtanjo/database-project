<template>
  <div v-loading="loading">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card class="stat-card" shadow="hover" @click="router.push(card.route)" style="cursor: pointer">
          <div class="stat-inner">
            <el-icon :size="36" :color="card.color"><component :is="card.icon" /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务状态分布 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="12">
        <el-card header="任务状态分布" shadow="never">
          <el-row :gutter="12">
            <el-col :span="6" v-for="item in taskStatus" :key="item.label">
              <div class="task-badge" :style="{ borderColor: item.color }">
                <div class="task-badge-count" :style="{ color: item.color }">{{ item.value }}</div>
                <div class="task-badge-label">{{ item.label }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="网页数 Top 网站" shadow="never">
          <el-table :data="topWebsites" size="small" :show-header="false">
            <el-table-column prop="domain" label="域名" />
            <el-table-column prop="webpage_count" label="网页数" width="80" align="right">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.webpage_count }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="topWebsites.length === 0" description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { List, Monitor, Document, Picture } from '@element-plus/icons-vue'
import { getStats } from '@/api/index'

const router = useRouter()

const loading = ref(false)
const stats = ref<any>(null)

const statCards = computed(() => {
  if (!stats.value) return []
  return [
    { label: '爬取任务', value: stats.value.tasks?.total ?? 0, icon: List, color: '#409eff', route: '/tasks' },
    { label: '已收录网站', value: stats.value.websites ?? 0, icon: Monitor, color: '#67c23a', route: '/websites' },
    { label: '内容条目', value: stats.value.contents ?? 0, icon: Document, color: '#e6a23c', route: '/contents' },
    { label: '图片数量', value: stats.value.images ?? 0, icon: Picture, color: '#f56c6c', route: '/images' },
  ]
})

const taskStatus = computed(() => {
  if (!stats.value) return []
  const t = stats.value.tasks ?? {}
  return [
    { label: '全部', value: t.total ?? 0, color: '#909399' },
    { label: '进行中', value: t.running ?? 0, color: '#409eff' },
    { label: '已完成', value: t.completed ?? 0, color: '#67c23a' },
    { label: '失败', value: t.failed ?? 0, color: '#f56c6c' },
  ]
})

const topWebsites = computed(() => stats.value?.top_websites ?? [])

async function fetchStats() {
  loading.value = true
  try {
    const res: any = await getStats()
    if (res.code === 0) stats.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>

<style scoped>
.stat-row {
  margin-bottom: 16px;
}
.stat-card {
  border-radius: 8px;
}
.stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-text {
  flex: 1;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 6px;
}
.section-row {
  margin-bottom: 16px;
}
.task-badge {
  border: 2px solid;
  border-radius: 8px;
  padding: 12px 8px;
  text-align: center;
}
.task-badge-count {
  font-size: 24px;
  font-weight: 700;
}
.task-badge-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>

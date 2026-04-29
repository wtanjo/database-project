<template>
  <div class="dashboard" v-loading="loading">

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div
        v-for="card in statCards"
        :key="card.label"
        class="stat-card"
        @click="router.push(card.route)"
      >
        <div class="stat-card-top">
          <span class="stat-label">{{ card.label }}</span>
          <div class="stat-icon-wrap" :style="{ background: card.bg }">
            <el-icon :size="18" :color="card.color"><component :is="card.icon" /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ card.value.toLocaleString() }}</div>
        <div class="stat-hint">点击查看详情 →</div>
      </div>
    </div>

    <!-- 下方两栏 -->
    <div class="bottom-grid">

      <!-- 任务状态 -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">任务状态</span>
          <el-tag size="small" type="info" round>共 {{ stats?.tasks?.total ?? 0 }} 条</el-tag>
        </div>
        <div class="status-list">
          <div v-for="item in taskStatus" :key="item.label" class="status-row">
            <div class="status-left">
              <span class="status-dot" :style="{ background: item.color }" />
              <span class="status-name">{{ item.label }}</span>
            </div>
            <div class="status-right">
              <div class="status-bar-track">
                <div
                  class="status-bar-fill"
                  :style="{
                    width: barWidth(item.value),
                    background: item.color,
                  }"
                />
              </div>
              <span class="status-count" :style="{ color: item.color }">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Top 网站 -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">网页数 Top 站点</span>
        </div>
        <div class="top-list">
          <div
            v-for="(site, i) in topWebsites"
            :key="site.domain"
            class="top-row"
          >
            <div class="top-rank" :class="{ gold: i === 0, silver: i === 1, bronze: i === 2 }">
              {{ i + 1 }}
            </div>
            <span class="top-domain">{{ site.domain }}</span>
            <span class="top-count">{{ site.webpage_count.toLocaleString() }}</span>
          </div>
          <el-empty v-if="topWebsites.length === 0" description="暂无数据" :image-size="48" />
        </div>
      </div>

    </div>
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
    {
      label: '爬取任务',
      value: stats.value.tasks?.total ?? 0,
      icon: List,
      color: '#d97757',
      bg: 'rgba(217,119,87,0.12)',
      route: '/tasks',
    },
    {
      label: '已收录网站',
      value: stats.value.websites ?? 0,
      icon: Monitor,
      color: '#7c6af5',
      bg: 'rgba(124,106,245,0.12)',
      route: '/websites',
    },
    {
      label: '内容条目',
      value: stats.value.contents ?? 0,
      icon: Document,
      color: '#2da44e',
      bg: 'rgba(45,164,78,0.12)',
      route: '/contents',
    },
    {
      label: '图片数量',
      value: stats.value.images ?? 0,
      icon: Picture,
      color: '#e06c75',
      bg: 'rgba(224,108,117,0.12)',
      route: '/images',
    },
  ]
})

const taskStatus = computed(() => {
  if (!stats.value) return []
  const t = stats.value.tasks ?? {}
  return [
    { label: '执行中', value: t.running ?? 0, color: '#7c6af5' },
    { label: '已完成', value: t.completed ?? 0, color: '#2da44e' },
    { label: '失败',   value: t.failed ?? 0,   color: '#e06c75' },
    { label: '排队中', value: (t.total ?? 0) - (t.running ?? 0) - (t.completed ?? 0) - (t.failed ?? 0), color: '#d97757' },
  ]
})

const topWebsites = computed(() => stats.value?.top_websites ?? [])

function barWidth(val: number) {
  const max = Number(stats.value?.tasks?.total) || 1
  return Math.max(4, Math.round((val / max) * 100)).toString() + '%'
}

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
/* ── layout ── */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── stat grid ── */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border: 1px solid #ede9e3;
  border-radius: 12px;
  padding: 20px 22px 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}
.stat-card:hover {
  box-shadow: 0 6px 24px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.stat-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  color: #8a8080;
  letter-spacing: 0.2px;
}

.stat-icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1a1614;
  line-height: 1;
  letter-spacing: -1px;
  margin-bottom: 10px;
}

.stat-hint {
  font-size: 11px;
  color: #c5bfb8;
}

/* ── bottom grid ── */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel {
  background: #fff;
  border: 1px solid #ede9e3;
  border-radius: 12px;
  padding: 20px 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1614;
}

/* ── status bars ── */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 70px;
  flex-shrink: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-name {
  font-size: 13px;
  color: #4a4540;
}

.status-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.status-bar-track {
  flex: 1;
  height: 6px;
  background: #f0ece6;
  border-radius: 99px;
  overflow: hidden;
}

.status-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.4s ease;
}

.status-count {
  font-size: 13px;
  font-weight: 600;
  width: 32px;
  text-align: right;
}

/* ── top list ── */
.top-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.top-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  transition: background 0.15s;
}
.top-row:hover { background: #faf8f5; }

.top-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #f0ece6;
  color: #8a8080;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.top-rank.gold   { background: #fff3cd; color: #b8860b; }
.top-rank.silver { background: #efefef; color: #708090; }
.top-rank.bronze { background: #fdebd0; color: #a0522d; }

.top-domain {
  flex: 1;
  font-size: 13px;
  color: #2c2825;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-count {
  font-size: 13px;
  font-weight: 600;
  color: #d97757;
  background: rgba(217,119,87,0.1);
  padding: 2px 8px;
  border-radius: 99px;
}
</style>

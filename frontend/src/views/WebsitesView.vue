<template>
  <div>
    <el-row :gutter="16">
      <!-- 网站列表 -->
      <el-col :span="10">
        <el-card header="网站列表" shadow="never">
          <el-table
            :data="websites"
            v-loading="websiteLoading"
            highlight-current-row
            @current-change="handleWebsiteSelect"
            size="small"
            border
          >
            <el-table-column prop="id" label="ID" width="55" align="center" />
            <el-table-column prop="domain" label="域名" show-overflow-tooltip />
            <el-table-column label="首次收录" width="100">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
          </el-table>
          <el-pagination
            class="pagination"
            v-model:current-page="websitePage"
            :page-size="10"
            :total="websiteTotal"
            layout="prev, pager, next"
            small
            @current-change="fetchWebsites"
          />
        </el-card>
      </el-col>

      <!-- 网页列表 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>
                网页列表
                <el-tag v-if="selectedWebsite" size="small" style="margin-left: 8px">
                  {{ selectedWebsite.domain }}
                </el-tag>
              </span>
              <el-button
                v-if="selectedWebsite"
                size="small"
                @click="clearFilter"
              >显示全部</el-button>
            </div>
          </template>

          <el-table :data="webpages" v-loading="webpageLoading" size="small" border>
            <el-table-column prop="id" label="ID" width="55" align="center" />
            <el-table-column prop="title" label="标题" show-overflow-tooltip width="140" />
            <el-table-column prop="url" label="URL" show-overflow-tooltip min-width="160" />
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="webpageStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" align="center">
              <template #default="{ row }">
                <el-popconfirm
                  title="删除该网页及其内容和图片？"
                  @confirm="handleDelete(row.id)"
                  width="200"
                >
                  <template #reference>
                    <el-button size="small" type="danger" :icon="Delete" circle />
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            class="pagination"
            v-model:current-page="webpagePage"
            :page-size="10"
            :total="webpageTotal"
            layout="prev, pager, next"
            small
            @current-change="fetchWebpages"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { getWebsites, getWebpages, deleteWebpage } from '@/api/index'

// ── Websites ─────────────────────────────────────────────────────────────────
const websites = ref<any[]>([])
const websiteLoading = ref(false)
const websitePage = ref(1)
const websiteTotal = ref(0)
const selectedWebsite = ref<any>(null)

async function fetchWebsites() {
  websiteLoading.value = true
  try {
    const res: any = await getWebsites(websitePage.value, 10)
    if (res.code === 0) {
      websites.value = res.data.items
      websiteTotal.value = res.data.total
    }
  } finally {
    websiteLoading.value = false
  }
}

function handleWebsiteSelect(row: any) {
  selectedWebsite.value = row
  webpagePage.value = 1
  fetchWebpages()
}

function clearFilter() {
  selectedWebsite.value = null
  webpagePage.value = 1
  fetchWebpages()
}

// ── Webpages ──────────────────────────────────────────────────────────────────
const webpages = ref<any[]>([])
const webpageLoading = ref(false)
const webpagePage = ref(1)
const webpageTotal = ref(0)

async function fetchWebpages() {
  webpageLoading.value = true
  try {
    const params: any = { page: webpagePage.value, page_size: 10 }
    if (selectedWebsite.value) params.website_id = selectedWebsite.value.id
    const res: any = await getWebpages(params)
    if (res.code === 0) {
      webpages.value = res.data.items
      webpageTotal.value = res.data.total
    }
  } finally {
    webpageLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    const res: any = await deleteWebpage(id)
    if (res.code === 0) {
      ElMessage.success('删除成功')
      fetchWebpages()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch {
    ElMessage.error('请求失败')
  }
}

function webpageStatusType(status: string) {
  const map: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    pending: 'info',
    fetching: 'warning',
  }
  return map[status] ?? ''
}

function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchWebsites()
  fetchWebpages()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination {
  margin-top: 12px;
  justify-content: flex-end;
}
</style>

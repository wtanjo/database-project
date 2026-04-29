<template>
  <div>
    <el-card shadow="never">
      <el-table
        :data="websites"
        v-loading="loading"
        border
        stripe
        @row-click="handleRowClick"
        row-class-name="clickable-row"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="domain" label="域名" />
        <el-table-column prop="organization" label="机构" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系方式" show-overflow-tooltip />
        <el-table-column label="首次收录" width="130">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="网页数" width="90" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.webpage_count ?? '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button size="small" @click.stop="goWebpages(row.domain)">查看网页</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchWebsites"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getWebsites } from '@/api/index'

const router = useRouter()
const websites = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function fetchWebsites() {
  loading.value = true
  try {
    const res: any = await getWebsites(page.value, pageSize.value)
    if (res.code === 0) {
      websites.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function handleRowClick(row: any) {
  goWebpages(row.domain)
}

function goWebpages(domain: string) {
  router.push({ path: '/webpages', query: { domain } })
}

onMounted(fetchWebsites)
</script>

<style scoped>
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
:deep(.clickable-row) { cursor: pointer; }
:deep(.clickable-row:hover td) { background-color: #ecf5ff !important; }
</style>

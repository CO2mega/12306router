<template>
  <div class="change-ticket-view">
    <div 
      v-loading="loading"
      element-loading-text="正在处理..."
      element-loading-background="rgba(255, 255, 255, 0.8)"
    >
      <div class="tabs-container">
        <div class="step-tabs">
          <div 
            class="tab-item" 
            :class="{ active: currentStep === 1 }"
            @click="stepTab(1)"
          >
            <span class="step-number">1</span>
            <span class="step-name">选择车票</span>
          </div>
          <div class="tab-divider"></div>
          <div 
            class="tab-item" 
            :class="{ active: currentStep === 2, disabled: !selectedTicket || actionType === '' }"
            @click="selectedTicket && actionType && stepTab(2)"
          >
            <span class="step-number">2</span>
            <span class="step-name">{{ actionType === 'change' ? '查询替换车次' : '退票确认' }}</span>
          </div>
          <div class="tab-divider"></div>
          <div 
            class="tab-item" 
            :class="{ 
              active: currentStep === 3, 
              disabled: !selectedNewTicket && actionType === 'change' 
            }"
            @click="(actionType === 'refund' || selectedNewTicket) && stepTab(3)"
          >
            <span class="step-number">3</span>
            <span class="step-name">确认信息</span>
          </div>
        </div>
      </div>

      <!-- 步骤1: 选择需要操作的车票 -->
      <div v-if="currentStep === 1" class="step-content">
        <h3 class="step-title">选择需要改签或退票的车票</h3>
        
        <div v-if="userTickets.length === 0" class="empty-tickets">
          <el-empty description="您还没有已购车票" :image-size="200">
            <el-button type="primary" @click="goToTicket">去购票</el-button>
          </el-empty>
        </div>
        
        <div v-else class="table-container">
          <el-table 
            :data="userTickets" 
            @row-click="handleTicketSelect"
            style="width: 100%"
            :fit="true"
            :show-overflow-tooltip="true"
            :header-cell-style="{background:'#f5f7fa', color:'#606266'}"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="trainCode" label="车次" width="100" />
            <el-table-column label="出发站" min-width="120">
              <template #default="{ row }">
                {{ row.fromStation }}
              </template>
            </el-table-column>
            <el-table-column label="到达站" min-width="120">
              <template #default="{ row }">
                {{ row.toStation }}
              </template>
            </el-table-column>
            <el-table-column prop="travelDate" label="出行日期" min-width="120" />
            <el-table-column prop="seatNumber" label="座位号" min-width="80" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <div class="action-btns">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click.stop="selectTicketToChange(row)"
                  >
                    改签
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click.stop="selectTicketToRefund(row)"
                  >
                    退票
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 步骤2: 查询替换车次或退票确认 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="selected-ticket-info">
          <h3 class="step-title">原车票信息</h3>
          <div class="ticket-info-card">
            <div class="info-item">
              <span class="label">车次:</span>
              <span class="value">{{ selectedTicket?.trainCode }}</span>
            </div>
            <div class="info-item">
              <span class="label">出发站:</span>
              <span class="value">{{ selectedTicket?.fromStation }}</span>
            </div>
            <div class="info-item">
              <span class="label">到达站:</span>
              <span class="value">{{ selectedTicket?.toStation }}</span>
            </div>
            <div class="info-item">
              <span class="label">出行日期:</span>
              <span class="value">{{ selectedTicket?.travelDate }}</span>
            </div>
            <div class="info-item">
              <span class="label">座位号:</span>
              <span class="value">{{ selectedTicket?.seatNumber }}</span>
            </div>
          </div>
        </div>

        <!-- 改签 - 查询替换车次 -->
        <template v-if="actionType === 'change'">
          <h3 class="step-title">查询替换车次</h3>
          <el-form :inline="true" class="ticket-form" @submit.prevent="handleSearch">
            <el-form-item label="出行日期">
              <el-date-picker
                v-model="searchForm.date"
                type="date"
                placeholder="选择日期"
                :disabled-date="disabledDate"
                :shortcuts="shortcuts"
                value-format="YYYY-MM-DD"
                :clearable="false"
                style="width: 180px"
              />
            </el-form-item>
            
            <el-form-item>
              <el-checkbox v-model="searchForm.isHighSpeed" @change="handleFilterChange">
                只看高铁/动车
              </el-checkbox>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
            </el-form-item>
          </el-form>

          <div class="table-container">
            <el-table 
              :data="filteredTickets" 
              v-loading="loading"
              style="width: 100%"
              :fit="true"
              :show-overflow-tooltip="true"
              :header-cell-style="{background:'#f5f7fa', color:'#606266'}"
            >
              <el-table-column prop="trainCode" label="车次" width="100" fixed="left" />
              <el-table-column label="出发站" min-width="140">
                <template #default="{ row }">
                  {{ row.from.station }} ({{ row.from.sequence }})
                </template>
              </el-table-column>
              <el-table-column label="到达站" min-width="140">
                <template #default="{ row }">
                  {{ row.to.station }} ({{ row.to.sequence }})
                </template>
              </el-table-column>
              <el-table-column prop="ticketsLeft" label="余票" min-width="80">
                <template #default="{ row }">
                  <span :class="{ 'text-warning': row.ticketsLeft < 20 }">
                    {{ row.ticketsLeft }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="runTime" label="全程运行时间" min-width="100" />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    size="small" 
                    :disabled="row.ticketsLeft <= 0"
                    @click="selectNewTicket(row)"
                  >
                    {{ row.ticketsLeft > 0 ? '选择此车次' : '已售完' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>

        <!-- 退票 - 退票确认 -->
        <template v-else-if="actionType === 'refund'">
          <h3 class="step-title">退票说明</h3>
          <div class="refund-notice">
            <div class="notice warning">
              <strong>退票须知:</strong>
              <ol>
                <li>距离发车时间超过48小时退票，不收取手续费</li>
                <li>距离发车时间24-48小时退票，收取票价5%的手续费</li>
                <li>距离发车时间2-24小时退票，收取票价10%的手续费</li>
                <li>距离发车时间不足2小时退票，收取票价20%的手续费</li>
                <li>开车后退票，不予受理</li>
              </ol>
            </div>

            <div class="refund-calculation">
              <h4>退款金额计算</h4>
              <div class="calculation-item">
                <span class="label">车票价格:</span>
                <span class="value">100 元</span>
              </div>
              <div class="calculation-item">
                <span class="label">手续费率:</span>
                <span class="value">5%</span>
              </div>
              <div class="calculation-item">
                <span class="label">手续费:</span>
                <span class="value">5 元</span>
              </div>
              <div class="calculation-item total">
                <span class="label">应退金额:</span>
                <span class="value">95 元</span>
              </div>
            </div>

            <div class="action-buttons">
              <el-button @click="currentStep = 1">返回</el-button>
              <el-button type="primary" @click="proceedToRefundConfirm">确认继续</el-button>
            </div>
          </div>
        </template>
      </div>

      <!-- 步骤3: 确认改签或退票信息 -->
      <div v-if="currentStep === 3" class="step-content">
        <!-- 改签确认 -->
        <template v-if="actionType === 'change'">
          <h3 class="step-title">确认改签信息</h3>
          
          <div class="comparison-container">
            <div class="ticket-card original">
              <div class="card-title">原车票信息</div>
              <div class="card-content">
                <div class="info-item">
                  <span class="label">车次:</span>
                  <span class="value">{{ selectedTicket?.trainCode }}</span>
                </div>
                <div class="info-item">
                  <span class="label">出发站:</span>
                  <span class="value">{{ selectedTicket?.fromStation }}</span>
                </div>
                <div class="info-item">
                  <span class="label">到达站:</span>
                  <span class="value">{{ selectedTicket?.toStation }}</span>
                </div>
                <div class="info-item">
                  <span class="label">出行日期:</span>
                  <span class="value">{{ selectedTicket?.travelDate }}</span>
                </div>
                <div class="info-item">
                  <span class="label">座位号:</span>
                  <span class="value">{{ selectedTicket?.seatNumber }}</span>
                </div>
              </div>
            </div>
            
            <div class="arrow-container">
              <i class="el-icon-arrow-right"></i>
            </div>
            
            <div class="ticket-card new">
              <div class="card-title">新车票信息</div>
              <div class="card-content">
                <div class="info-item">
                  <span class="label">车次:</span>
                  <span class="value">{{ selectedNewTicket?.trainCode }}</span>
                </div>
                <div class="info-item">
                  <span class="label">出发站:</span>
                  <span class="value">{{ selectedNewTicket?.from.station }}</span>
                </div>
                <div class="info-item">
                  <span class="label">到达站:</span>
                  <span class="value">{{ selectedNewTicket?.to.station }}</span>
                </div>
                <div class="info-item">
                  <span class="label">出行日期:</span>
                  <span class="value">{{ searchForm.date }}</span>
                </div>
                <div class="info-item">
                  <span class="label">座位号:</span>
                  <span class="value">待分配</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="notice">
            <strong>改签须知:</strong>
            <ol>
              <li>改签完成后，原车票将自动作废</li>
              <li>若新车次票价高于原车次，需补差价</li>
              <li>若新车次票价低于原车次，差价将退还至您的账户</li>
              <li>改签后座位号将重新分配</li>
            </ol>
          </div>
          
          <div class="action-buttons">
            <el-button @click="currentStep = 2">返回修改</el-button>
            <el-button type="primary" @click="confirmChange" :loading="confirmLoading">确认改签</el-button>
          </div>
        </template>

        <!-- 退票确认 -->
        <template v-else-if="actionType === 'refund'">
          <h3 class="step-title">确认退票信息</h3>
          
          <div class="refund-confirmation">
            <div class="ticket-card original">
              <div class="card-title">退票车次信息</div>
              <div class="card-content">
                <div class="info-item">
                  <span class="label">车次:</span>
                  <span class="value">{{ selectedTicket?.trainCode }}</span>
                </div>
                <div class="info-item">
                  <span class="label">出发站:</span>
                  <span class="value">{{ selectedTicket?.fromStation }}</span>
                </div>
                <div class="info-item">
                  <span class="label">到达站:</span>
                  <span class="value">{{ selectedTicket?.toStation }}</span>
                </div>
                <div class="info-item">
                  <span class="label">出行日期:</span>
                  <span class="value">{{ selectedTicket?.travelDate }}</span>
                </div>
                <div class="info-item">
                  <span class="label">座位号:</span>
                  <span class="value">{{ selectedTicket?.seatNumber }}</span>
                </div>
              </div>
            </div>

            <div class="refund-calculation">
              <h4>退款金额确认</h4>
              <div class="calculation-item">
                <span class="label">车票价格:</span>
                <span class="value">100 元</span>
              </div>
              <div class="calculation-item">
                <span class="label">手续费率:</span>
                <span class="value">5%</span>
              </div>
              <div class="calculation-item">
                <span class="label">手续费:</span>
                <span class="value">5 元</span>
              </div>
              <div class="calculation-item total">
                <span class="label">应退金额:</span>
                <span class="value">95 元</span>
              </div>
            </div>
          </div>
          
          <div class="notice danger">
            <strong>退票提示:</strong>
            <p>退票完成后，车票将立即作废且无法恢复。请确认您的退票决定。</p>
          </div>
          
          <div class="action-buttons">
            <el-button @click="currentStep = 2">返回</el-button>
            <el-button type="danger" @click="confirmRefund" :loading="confirmLoading">确认退票</el-button>
          </div>
        </template>
      </div>
      
      <!-- 操作成功提示 -->
      <el-dialog
        v-model="operationSuccess"
        :title="actionType === 'change' ? '改签成功' : '退票成功'"
        width="30%"
        :close-on-click-modal="false"
        :show-close="false"
      >
        <div class="success-content">
          <i class="el-icon-success"></i>
          <h3>{{ actionType === 'change' ? '车票改签成功!' : '车票退票成功!' }}</h3>
          <p v-if="actionType === 'change'">您的新车票信息已生成，请在个人中心查看</p>
          <p v-else>退款将在1-7个工作日内退回至您的支付账户</p>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="viewUserProfile">查看个人中心</el-button>
            <el-button type="primary" @click="operationSuccess = false">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const confirmLoading = ref(false)
const currentStep = ref(1)
const userTickets = ref([])
const selectedTicket = ref(null)
const selectedNewTicket = ref(null)
const operationSuccess = ref(false)
const actionType = ref('') // 'change' 或 'refund'

// 初始化搜索表单
const searchForm = reactive({
  from: '',
  to: '',
  date: new Date().toISOString().slice(0, 10),
  isHighSpeed: false
})

// 原始车票数据
const tickets = ref([])

// 过滤后的车票数据
const filteredTickets = computed(() => {
  if (!searchForm.isHighSpeed) {
    return tickets.value;
  }
  
  // 只返回G或D开头的车次
  return tickets.value.filter(ticket => {
    const trainCode = ticket.trainCode.toUpperCase();
    return trainCode.startsWith('G') || trainCode.startsWith('D');
  });
})

// 日期选择器的禁用日期范围
const disabledDate = (time) => {
  // 获取今天的起始时间（0时0分0秒）
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  // 获取30天后的结束时间（23时59分59秒）
  const maxDate = new Date()
  maxDate.setDate(today.getDate() + 30)
  maxDate.setHours(23, 59, 59, 999)
  
  return time.getTime() < today.getTime() || time.getTime() > maxDate.getTime()
}

// 计算日期选择器的快捷选项
const shortcuts = [
  {
    text: '今天',
    value: new Date(),
  },
  {
    text: '明天',
    value: (() => {
      const date = new Date()
      date.setDate(date.getDate() + 1)
      return date
    })(),
  },
  {
    text: '后天',
    value: (() => {
      const date = new Date()
      date.setDate(date.getDate() + 2)
      return date
    })(),
  },
  {
    text: '一周后',
    value: (() => {
      const date = new Date()
      date.setDate(date.getDate() + 7)
      return date
    })(),
  }
]

// 步骤切换
function stepTab(step) {
  currentStep.value = step
}

// 获取用户已购车票
async function fetchUserTickets() {
  loading.value = true
  try {
    const { data } = await request.get('/api/user/tickets')
    
    if (data.code === 0) {
      userTickets.value = data.data.tickets
    } else {
      ElMessage.error(data.msg || '获取车票信息失败')
    }
  } catch (error) {
    console.error('获取用户车票错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 选择需要改签的车票
function selectTicketToChange(ticket) {
  selectedTicket.value = ticket;
  actionType.value = 'change';

  searchForm.date = ticket.travelDate;
  currentStep.value = 2;
}

// 选择需要退票的车票
function selectTicketToRefund(ticket) {
  selectedTicket.value = ticket
  actionType.value = 'refund'
  currentStep.value = 2
}

// 处理表格行点击
function handleTicketSelect(row) {
  // 不在行点击时自动选择操作类型，让用户通过按钮明确选择
}

// 处理过滤变化
function handleFilterChange() {
  // 只是UI层面的过滤，无需重新请求数据
}

// 查询替换车次
const handleSearch = async () => {
  if (!selectedTicket.value) {
    ElMessage.warning('请先选择需要改签的车票');
    return;
  }

  loading.value = true;
  try {
    // 转换站点名为城市名
    const fromCity = stationToCity(selectedTicket.value.fromStation);
    const toCity = stationToCity(selectedTicket.value.toStation);
    
    console.log(`查询路线: 从${fromCity}到${toCity}, 日期: ${searchForm.date}`);
    
    const { data } = await request.get('/api/routes/direct', {
      params: {
        from: fromCity,  // 使用城市名代替站点名
        to: toCity,      // 使用城市名代替站点名
        date: searchForm.date
      }
    });

    if (data.code === 0) {
      tickets.value = data.data.routes;
      if (tickets.value.length === 0) {
        ElMessage.info('未找到符合条件的车次');
      } else if (searchForm.isHighSpeed && filteredTickets.value.length === 0) {
        ElMessage.info('未找到符合条件的高铁/动车');
      }
    } else {
      ElMessage.error(data.msg || '查询失败');
    }
  } catch (error) {
    console.error('查询错误:', error);
    ElMessage.error('网络错误，请稍后重试');
  } finally {
    loading.value = false;
  }
}

// 选择新的车票
function selectNewTicket(ticket) {
  selectedNewTicket.value = ticket
  currentStep.value = 3
}

// 进入退票确认步骤
function proceedToRefundConfirm() {
  currentStep.value = 3
}

// 确认改签
async function confirmChange() {
  if (!selectedTicket.value || !selectedNewTicket.value) {
    ElMessage.warning('请先完成车票选择')
    return
  }

  confirmLoading.value = true
  try {
    const { data } = await request.post('/api/tickets/change', {
      ticketId: selectedTicket.value.id,
      newTrainCode: selectedNewTicket.value.trainCode,
      newTrainFullCode: selectedNewTicket.value.trainFullCode,
      newFromStation: selectedNewTicket.value.from.station,
      newToStation: selectedNewTicket.value.to.station,
      newFromStationNo: selectedNewTicket.value.from.sequence,
      newToStationNo: selectedNewTicket.value.to.sequence,
      newTravelDate: searchForm.date
    })

    if (data.code === 0) {
      operationSuccess.value = true
      // 改签成功后重置状态
      resetOperationState()
    } else {
      ElMessage.error(data.msg || '改签失败')
    }
  } catch (error) {
    console.error('改签错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    confirmLoading.value = false
  }
}

// 确认退票
async function confirmRefund() {
  if (!selectedTicket.value) {
    ElMessage.warning('请选择需要退票的车票')
    return
  }

  confirmLoading.value = true
  try {
    const { data } = await request.post('/api/tickets/refund', {
      ticketId: selectedTicket.value.id
    })

    if (data.code === 0) {
      operationSuccess.value = true
      // 退票成功后重置状态
      resetOperationState()
    } else {
      ElMessage.error(data.msg || '退票失败')
    }
  } catch (error) {
    console.error('退票错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    confirmLoading.value = false
  }
}

// 重置操作状态
function resetOperationState() {
  currentStep.value = 1
  selectedTicket.value = null
  selectedNewTicket.value = null
  tickets.value = []
  actionType.value = ''
  fetchUserTickets() // 重新获取用户车票
}

// 查看个人中心
function viewUserProfile() {
  router.push('/user-profile')
  operationSuccess.value = false
}

// 前往购票页面
function goToTicket() {
  router.push('/ticket')
}

// 组件挂载时获取用户车票
onMounted(() => {
  fetchUserTickets()
})

// 添加站点名到城市名的映射
function stationToCity(stationName) {
  // 常见站点与城市映射
  const stationCityMap = {
    '北京': '北京',
    '北京南': '北京',
    '北京西': '北京',
    '北京东': '北京',
    '北京北': '北京',
    '上海': '上海',
    '上海南': '上海',
    '上海虹桥': '上海',
    '广州': '广州',
    '广州南': '广州',
    '广州东': '广州',
    '深圳': '深圳',
    '深圳北': '深圳',
    '天津': '天津',
    '天津西': '天津',
    '天津南': '天津',
    '杭州': '杭州',
    '杭州东': '杭州',
    '南京': '南京',
    '南京南': '南京',
    '武汉': '武汉',
    '成都': '成都',
    '成都东': '成都',
    '西安': '西安',
    '西安北': '西安',
    '重庆': '重庆',
    '重庆北': '重庆',
    '郑州': '郑州',
    '郑州东': '郑州',
    '济南': '济南',
    '济南西': '济南',
    '长沙': '长沙',
    '长沙南': '长沙',
    // 可以根据需要添加更多映射
  };
  
  // 如果找到映射，返回城市名；否则返回原站点名
  return stationCityMap[stationName] || stationName;
}
</script>

<style scoped>
/* 改签页面基本样式 */
.change-ticket-view {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #fff;
  padding: 20px 80px 100px;
  box-sizing: border-box;
  margin: 0 auto 120px auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

/* 步骤导航标签 */
.tabs-container {
  margin-bottom: 30px;
  width: 100%;
  max-width: 1500px;
  margin-left: auto;
  margin-right: auto;
}

.step-tabs {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.tab-item {
  display: flex;
  align-items: center;
  padding: 0 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-item.active {
  color: #409eff;
  font-weight: bold;
}

.tab-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #e6e6e6;
  color: #606266;
  margin-right: 10px;
}

.tab-item.active .step-number {
  background: #409eff;
  color: #fff;
}

.tab-divider {
  flex-grow: 0;
  width: 100px;
  height: 2px;
  background: #e6e6e6;
  margin: 0 15px;
}

/* 步骤内容区域 */
.step-content {
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
}

.step-title {
  margin-bottom: 20px;
  color: #303133;
  font-size: 18px;
  font-weight: bold;
}

/* 表格样式 */
.table-container {
  width: 100%;
  margin-top: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.03);
}

/* 票务卡片样式 */
.ticket-info-card {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 30px;
  border: 1px solid #e6e6e6;
}

.info-item {
  margin-bottom: 12px;
  line-height: 24px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  display: inline-block;
  width: 80px;
  color: #909399;
}

.info-item .value {
  font-weight: 500;
  color: #303133;
}

/* 票务表单 */
.ticket-form {
  background: #f5f7fa;
  padding: 25px;
  border-radius: 4px;
  margin-bottom: 30px;
  border: 1px solid #e6e6e6;
}

/* 改签对比区域 */
.comparison-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 40px;
}

.ticket-card {
  width: 40%;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.ticket-card.original {
  background-color: #f5f7fa;
  border: 1px solid #e6e6e6;
}

.ticket-card.new {
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
  color: #303133;
}

.arrow-container {
  font-size: 24px;
  color: #409eff;
  display: flex;
  align-items: center;
}

/* 改签须知 */
.notice {
  padding: 20px;
  background: #fdf6ec;
  border-radius: 4px;
  margin-bottom: 30px;
  color: #e6a23c;
  border: 1px solid #faecd8;
}

.notice strong {
  display: block;
  margin-bottom: 10px;
}

.notice ol {
  margin: 0;
  padding-left: 20px;
}

.notice li {
  margin-bottom: 5px;
}

.notice li:last-child {
  margin-bottom: 0;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

/* 改签成功提示 */
.success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.success-content i {
  font-size: 50px;
  color: #67c23a;
  margin-bottom: 15px;
}

.success-content h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #67c23a;
}

.success-content p {
  margin: 0;
  color: #606266;
}

/* 空车票提示 */
.empty-tickets {
  padding: 50px 0;
  display: flex;
  justify-content: center;
}

/* 确保表格样式一致 */
:deep(.el-table) {
  width: 100%;
}

:deep(.el-table__header) {
  background-color: #f5f7fa;
}

/* 高亮行效果 */
:deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}

/* 警告文字样式 */
.text-warning {
  color: #e6a23c;
  font-weight: bold;
}

/* 响应式调整 */
@media screen and (max-width: 1600px) {
  .change-ticket-view {
    padding: 20px 30px 80px;
  }
  
  .step-content, .tabs-container {
    max-width: 95%;
  }
  
  .comparison-container {
    flex-direction: column;
    gap: 30px;
  }
  
  .ticket-card {
    width: 80%;
  }
  
  .arrow-container {
    transform: rotate(90deg);
    margin: 10px 0;
  }
}

/* 窄屏幕适配 */
@media screen and (max-width: 768px) {
  .tab-divider {
    width: 60px;
  }
  
  .step-tabs {
    padding: 15px 5px;
  }
  
  .tab-item {
    padding: 0 5px;
  }
  
  .step-name {
    font-size: 14px;
  }
}

.action-btns {
  display: flex;
  gap: 8px;
}

.refund-notice {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.notice.warning {
  background: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #faecd8;
}

.notice.danger {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fde2e2;
}

.refund-calculation {
  background: #f5f7fa;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 20px;
  margin: 30px 0;
}

.refund-calculation h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.calculation-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ebeef5;
}

.calculation-item:last-child {
  border-bottom: none;
}

.calculation-item.total {
  font-weight: bold;
  color: #303133;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.refund-confirmation {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-bottom: 30px;
}

.refund-confirmation .ticket-card {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

@media screen and (max-width: 768px) {
  .action-btns {
    flex-direction: column;
    gap: 5px;
  }
}
</style>
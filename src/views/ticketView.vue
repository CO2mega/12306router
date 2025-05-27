<template>
  <div class="ticket-view">
    <h2>车票查询</h2>
    <el-form :inline="true" class="ticket-form">
      <el-form-item label="出发地">
        <el-input placeholder="请输入出发地"></el-input>
      </el-form-item>
      <el-form-item label="目的地">
        <el-input placeholder="请输入目的地"></el-input>
      </el-form-item>
      <el-form-item label="日期">
        <el-date-picker type="date" placeholder="选择日期"></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary">查询</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="[]" style="width: 100%; margin-top: 24px">
      <el-table-column prop="train" label="车次" width="120" />
      <el-table-column prop="from" label="出发站" width="120" />
      <el-table-column prop="to" label="到达站" width="120" />
      <el-table-column prop="time" label="发车时间" width="120" />
      <el-table-column prop="price" label="票价" width="120" />
      <el-table-column label="操作" width="120">
        <template #default>
          <el-button type="primary" size="small">预订</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
// 可根据需要添加逻辑
</script>

<style scoped>
.ticket-view {
  width: 100vw;
  min-height: calc(100vh - 64px);
  background: #fff;
  padding: 32px 5vw;
  box-sizing: border-box;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
  overflow-x: auto;
}
.ticket-form {
  margin-bottom: 24px;
}
</style>

<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" class="pa-6">
          <v-card-title class="text-h4 text-center mb-6">
            {{ $t('resetPassword.title') }}
          </v-card-title>
          
          <v-card-subtitle class="text-center mb-4">
            {{ $t('resetPassword.subtitle') }}
          </v-card-subtitle>
          
          <!-- 錯誤訊息 -->
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="errorMessage = ''"
          >
            {{ errorMessage }}
          </v-alert>
          
          <!-- 成功訊息 -->
          <v-alert
            v-if="successMessage"
            type="success"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="successMessage = ''"
          >
            {{ successMessage }}
          </v-alert>
          
          <v-form @submit.prevent="handleResetPassword" ref="form">
            <v-text-field
              v-model="resetData.token"
              :label="$t('resetPassword.resetCode')"
              :rules="tokenRules"
              required
              prepend-inner-icon="mdi-key"
              variant="outlined"
              class="mb-4"
              :readonly="tokenFromUrl"
            ></v-text-field>
            
            <v-text-field
              v-model="resetData.newPassword"
              :label="$t('resetPassword.newPassword')"
              :type="showPassword ? 'text' : 'password'"
              :rules="passwordRules"
              required
              prepend-inner-icon="mdi-lock"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPassword = !showPassword"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="resetData.confirmPassword"
              :label="$t('resetPassword.confirmPassword')"
              :type="showConfirmPassword ? 'text' : 'password'"
              :rules="confirmPasswordRules"
              required
              prepend-inner-icon="mdi-lock-check"
              :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showConfirmPassword = !showConfirmPassword"
              variant="outlined"
              class="mb-6"
            ></v-text-field>
            
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="loading"
              prepend-icon="mdi-key-change"
            >
              {{ $t('resetPassword.resetPassword') }}
            </v-btn>
          </v-form>
          
          <v-divider class="my-6"></v-divider>
          
          <div class="text-center">
            <p class="text-body-2 mb-2">{{ $t('resetPassword.rememberPassword') }}</p>
            <v-btn
              variant="outlined"
              color="primary"
              @click="$router.push('/login')"
              prepend-icon="mdi-arrow-left"
            >
              {{ $t('auth.login') }}
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const form = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const tokenFromUrl = ref(false)

const resetData = reactive({
  token: '',
  newPassword: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)

// 驗證規則
const tokenRules = [
  v => !!v || t('resetPassword.validation.tokenRequired')
]

const passwordRules = [
  v => !!v || t('resetPassword.validation.passwordRequired'),
  v => (v && v.length >= 6) || t('resetPassword.validation.passwordMinLength')
]

const confirmPasswordRules = [
  v => !!v || t('resetPassword.validation.confirmPasswordRequired'),
  v => v === resetData.newPassword || t('resetPassword.validation.passwordMismatch')
]

// 重設密碼
const handleResetPassword = async () => {
  if (!resetData.token || !resetData.newPassword || !resetData.confirmPassword) return
  
  // 清除之前的訊息
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true
  
  try {
    const response = await api.post('/auth/reset-password', {
      token: resetData.token,
      new_password: resetData.newPassword
    })
    
    // 顯示成功訊息
    successMessage.value = response.data.message
    
    // 等待一下讓用戶看到成功訊息，然後跳轉到登入頁面
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (error) {
    console.error('重設密碼失敗:', error)
    
    let errorMsg = '重設密碼失敗，請檢查重設碼是否正確'
    
    if (error.response && error.response.data?.detail) {
      errorMsg = error.response.data.detail
    }
    
    errorMessage.value = errorMsg
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 從 URL 參數中獲取重設令牌
  const token = route.query.token
  if (token) {
    resetData.token = token
    tokenFromUrl.value = true
  }
})
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.v-card {
  border-radius: 12px;
}
</style>

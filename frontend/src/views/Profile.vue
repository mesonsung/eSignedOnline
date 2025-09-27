<template>
  <v-container class="pa-6">
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="themed-card hover-lift">
          <v-card-title class="text-h5 pa-6">
            <v-icon class="mr-3" color="primary">mdi-account-circle</v-icon>
            <span class="text-gradient">{{ $t('profile.title') }}</span>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <!-- 基本資訊 -->
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="userInfo.username"
                  :label="$t('auth.username')"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  readonly
                  class="mb-4"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="userInfo.email"
                  :label="$t('auth.email')"
                  prepend-inner-icon="mdi-email"
                  variant="outlined"
                  readonly
                  class="mb-4"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <v-text-field
              v-model="userInfo.full_name"
              :label="$t('auth.fullName')"
              prepend-inner-icon="mdi-account-circle"
              variant="outlined"
              readonly
              class="mb-4"
            ></v-text-field>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-chip
                  :color="userInfo.role === 'admin' ? 'primary' : 'secondary'"
                  variant="tonal"
                >
                  <v-icon class="mr-2">
                    {{ userInfo.role === 'admin' ? 'mdi-crown' : 'mdi-account' }}
                  </v-icon>
                  {{ $t(`role.${userInfo.role}`) }}
                </v-chip>
              </v-col>
              <v-col cols="12" md="6">
                <v-chip
                  :color="userInfo.is_active ? 'success' : 'warning'"
                  variant="tonal"
                >
                  <v-icon class="mr-2">
                    {{ userInfo.is_active ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                  </v-icon>
                  {{ userInfo.is_active ? $t('user.active') : $t('user.inactive') }}
                </v-chip>
              </v-col>
            </v-row>
            
            <v-row class="mt-4">
              <v-col cols="12" md="6">
                <v-text-field
                  :model-value="formatDate(userInfo.created_at)"
                  :label="$t('profile.createdAt')"
                  prepend-inner-icon="mdi-calendar-plus"
                  variant="outlined"
                  readonly
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  :model-value="formatDate(userInfo.updated_at)"
                  :label="$t('profile.updatedAt')"
                  prepend-inner-icon="mdi-calendar-edit"
                  variant="outlined"
                  readonly
                ></v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
          
          <v-divider></v-divider>
          
          <!-- 修改密碼區域 -->
          <v-card-text class="pa-6">
            <h3 class="text-h6 mb-4">
              <v-icon class="mr-3">mdi-lock</v-icon>
              {{ $t('profile.changePassword') }}
            </h3>
            
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
            
            <v-form @submit.prevent="changePassword" ref="passwordForm">
              <v-text-field
                v-model="passwordData.oldPassword"
                :label="$t('profile.oldPassword')"
                :type="showOldPassword ? 'text' : 'password'"
                :rules="oldPasswordRules"
                required
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="showOldPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showOldPassword = !showOldPassword"
                variant="outlined"
                class="mb-4"
              ></v-text-field>
              
              <v-text-field
                v-model="passwordData.newPassword"
                :label="$t('profile.newPassword')"
                :type="showNewPassword ? 'text' : 'password'"
                :rules="newPasswordRules"
                required
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showNewPassword = !showNewPassword"
                variant="outlined"
                class="mb-4"
              ></v-text-field>
              
              <v-text-field
                v-model="passwordData.confirmPassword"
                :label="$t('profile.confirmPassword')"
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
                :loading="passwordLoading"
                :disabled="passwordLoading"
                prepend-icon="mdi-key-change"
              >
                {{ $t('profile.changePassword') }}
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const passwordForm = ref(null)
const userInfo = reactive({
  username: '',
  email: '',
  full_name: '',
  role: '',
  is_active: false,
  created_at: '',
  updated_at: ''
})

const passwordData = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 驗證規則
const oldPasswordRules = [
  v => !!v || t('profile.validation.oldPasswordRequired')
]

const newPasswordRules = [
  v => !!v || t('profile.validation.newPasswordRequired'),
  v => (v && v.length >= 6) || t('profile.validation.passwordMinLength')
]

const confirmPasswordRules = [
  v => !!v || t('profile.validation.confirmPasswordRequired'),
  v => v === passwordData.newPassword || t('profile.validation.passwordMismatch')
]

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 載入用戶資訊
const loadUserInfo = async () => {
  try {
    // 從 authStore 中獲取用戶資訊
    if (authStore.user) {
      Object.assign(userInfo, authStore.user)
    } else {
      // 如果 authStore 中沒有用戶資訊，從 API 獲取
      await authStore.fetchUser()
      Object.assign(userInfo, authStore.user)
    }
  } catch (error) {
    console.error('載入用戶資訊失敗:', error)
    errorMessage.value = '載入用戶資訊失敗'
  }
}

// 修改密碼
const changePassword = async () => {
  if (!passwordData.oldPassword || !passwordData.newPassword || !passwordData.confirmPassword) return
  
  // 清除之前的訊息
  errorMessage.value = ''
  successMessage.value = ''
  passwordLoading.value = true
  
  try {
    await api.post('/auth/change-password', {
      old_password: passwordData.oldPassword,
      new_password: passwordData.newPassword
    })
    
    // 顯示成功訊息
    successMessage.value = '密碼修改成功！'
    
    // 清空表單
    passwordData.oldPassword = ''
    passwordData.newPassword = ''
    passwordData.confirmPassword = ''
    
    // 重設表單驗證狀態
    if (passwordForm.value) {
      passwordForm.value.reset()
    }
    
  } catch (error) {
    console.error('修改密碼失敗:', error)
    
    let errorMsg = '修改密碼失敗，請稍後重試'
    
    if (error.response && error.response.data?.detail) {
      errorMsg = error.response.data.detail
    }
    
    errorMessage.value = errorMsg
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-chip {
  font-weight: 500;
}
</style>

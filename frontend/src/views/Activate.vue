<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" class="pa-6">
          <v-card-title class="text-h4 text-center mb-6">
            {{ $t('auth.activate') }}
          </v-card-title>
          
          <v-alert
            type="info"
            variant="tonal"
            class="mb-6"
          >
            {{ $t('auth.activateInstructions') }}
          </v-alert>
          
          <v-form @submit.prevent="handleActivate" ref="form">
            <v-text-field
              v-model="formData.username"
              :label="$t('auth.username')"
              :rules="usernameRules"
              required
              prepend-inner-icon="mdi-account"
              variant="outlined"
              class="mb-4"
              :disabled="!!$route.query.username"
            ></v-text-field>
            
            <v-text-field
              v-model="formData.activationCode"
              :label="$t('auth.activationCode')"
              :rules="activationCodeRules"
              required
              prepend-inner-icon="mdi-key"
              variant="outlined"
              class="mb-6"
              placeholder="輸入8位啟用碼"
            ></v-text-field>
            
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="loading"
            >
              {{ $t('auth.activate') }}
            </v-btn>
          </v-form>
          
          <v-divider class="my-6"></v-divider>
          
          <div class="text-center">
            <p class="text-body-2 mb-2">{{ $t('auth.activateSuccessMessage') }}</p>
            <v-btn
              variant="outlined"
              color="primary"
              @click="$router.push('/login')"
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
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const form = ref(null)
const formData = reactive({
  username: '',
  activationCode: ''
})

const loading = ref(false)

const usernameRules = [
  v => !!v || t('auth.validation.usernameRequired')
]

const activationCodeRules = [
  v => !!v || t('auth.validation.activationCodeRequired'),
  v => (v && v.length === 8) || t('auth.validation.activationCodeLength')
]

const handleActivate = async () => {
  if (!formData.username || !formData.activationCode) return
  
  loading.value = true
  
  try {
    await authStore.activate(formData.username, formData.activationCode)
    
    // 啟用成功後跳轉到登入頁面
    router.push('/login')
  } catch (error) {
    console.error('Activate error:', error)
    // 這裡可以顯示錯誤訊息
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 如果 URL 中有 username 參數，自動填入
  if (router.currentRoute.value.query.username) {
    formData.username = router.currentRoute.value.query.username
  }
})
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>

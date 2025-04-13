import { useState } from 'react'
import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Snackbar
} from '@mui/material'
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query'
import { fetchHotRepos, trackRepo } from './api/github'
import { Repo } from './types'

const queryClient = new QueryClient()

// 将主要内容移到单独的组件中
function MainContent() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const { data: repos = [], refetch, isLoading } = useQuery({
    queryKey: ['hotRepos'],
    queryFn: fetchHotRepos,
    enabled: true,  // 改为 true，使其在页面加载时自动获取数据
    refetchOnWindowFocus: false  // 窗口获得焦点时不自动刷新
  })

  // 添加追踪仓库的 mutation
  const trackMutation = useMutation({
    mutationFn: trackRepo,
    onSuccess: () => {
      setMessage('仓库追踪成功！')
    },
    onError: (error) => {
      setMessage('追踪失败：' + (error as Error).message)
    }
  })

  const handleRefreshRepos = async () => {
    setLoading(true)
    try {
      await refetch()
      setMessage('数据刷新成功！')
    } catch (error) {
      console.error('Error refreshing repos:', error)
      setMessage('刷新失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleTrackRepo = (repoFullName: string) => {
    trackMutation.mutate(repoFullName)
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          GitHub 热门项目追踪
        </Typography>
        
        <Box sx={{ mb: 4 }}>
          <Button 
            variant="contained" 
            onClick={handleRefreshRepos}
            disabled={loading || isLoading}
            sx={{ mr: 2 }}
          >
            {(loading || isLoading) ? <CircularProgress size={24} color="inherit" /> : '刷新项目动态'}
          </Button>
        </Box>

        <TableContainer component={Paper}>
          {isLoading ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <CircularProgress />
              <Typography sx={{ mt: 2 }}>正在加载项目数据...</Typography>
            </Box>
          ) : (
            <Table sx={{ minWidth: 650 }} aria-label="热门项目表格">
              <TableHead>
                <TableRow>
                  <TableCell>项目名称</TableCell>
                  <TableCell>描述</TableCell>
                  <TableCell align="right">Stars</TableCell>
                  <TableCell align="right">Forks</TableCell>
                  <TableCell align="right">最近更新</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {repos.map((repo: Repo) => (
                  <TableRow key={repo.full_name}>
                    <TableCell component="th" scope="row">
                      <Typography variant="body2" component="div">
                        <strong>{repo.name}</strong>
                        <br />
                        <small>{repo.full_name}</small>
                      </Typography>
                    </TableCell>
                    <TableCell>{repo.description}</TableCell>
                    <TableCell align="right">{repo.stars}</TableCell>
                    <TableCell align="right">{repo.forks}</TableCell>
                    <TableCell align="right">
                      {new Date(repo.updated_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Button 
                        variant="outlined" 
                        size="small"
                        onClick={() => handleTrackRepo(repo.full_name)}
                        disabled={trackMutation.isPending}
                      >
                        {trackMutation.isPending ? '追踪中...' : '追踪'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TableContainer>
      </Box>

      <Snackbar
        open={!!message}
        autoHideDuration={3000}
        onClose={() => setMessage('')}
      >
        <Alert 
          severity={message.includes('成功') ? 'success' : 'error'} 
          onClose={() => setMessage('')}
        >
          {message}
        </Alert>
      </Snackbar>
    </Container>
  )
}

// App 组件现在只负责提供 QueryClientProvider
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainContent />
    </QueryClientProvider>
  )
}

export default App

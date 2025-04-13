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
  Snackbar,
  Tabs,
  Tab,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material'
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query'
import { fetchHotRepos, trackRepo, fetchTrackedRepos, untrackRepo } from './api/github'
import { Repo, TrackedRepo } from './types'

const queryClient = new QueryClient()

// 定义标签页接口
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// 将主要内容移到单独的组件中
function MainContent() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [tabValue, setTabValue] = useState(0)
  const [selectedRepo, setSelectedRepo] = useState<TrackedRepo | null>(null)
  const [activityDialogOpen, setActivityDialogOpen] = useState(false)

  // 热门仓库查询
  const { 
    data: hotRepos = [], 
    refetch: refetchHotRepos, 
    isLoading: isLoadingHotRepos 
  } = useQuery({
    queryKey: ['hotRepos'],
    queryFn: fetchHotRepos,
    enabled: true,
    refetchOnWindowFocus: false
  })

  // 跟踪的仓库查询
  const { 
    data: trackedRepos = [], 
    refetch: refetchTrackedRepos,
    isLoading: isLoadingTrackedRepos 
  } = useQuery({
    queryKey: ['trackedRepos'],
    queryFn: fetchTrackedRepos,
    enabled: true,
    refetchOnWindowFocus: false
  })

  // 添加跟踪仓库的 mutation
  const trackMutation = useMutation({
    mutationFn: trackRepo,
    onSuccess: () => {
      setMessage('仓库跟踪成功！')
      refetchTrackedRepos() // 刷新跟踪列表
    },
    onError: (error) => {
      setMessage('跟踪失败：' + (error as Error).message)
    }
  })

  // 取消跟踪仓库的 mutation
  const untrackMutation = useMutation({
    mutationFn: untrackRepo,
    onSuccess: () => {
      setMessage('已取消跟踪！')
      refetchTrackedRepos() // 刷新跟踪列表
    },
    onError: (error) => {
      setMessage('取消跟踪失败：' + (error as Error).message)
    }
  })

  const handleRefreshRepos = async () => {
    setLoading(true)
    try {
      await refetchHotRepos()
      setMessage('数据刷新成功！')
    } catch (error) {
      console.error('Error refreshing repos:', error)
      setMessage('刷新失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleTrackRepo = (repoFullName: string) => {
    trackMutation.mutate(repoFullName)
  }

  const handleUntrackRepo = (repoFullName: string) => {
    untrackMutation.mutate(repoFullName)
  }

  const handleShowActivities = (repo: TrackedRepo) => {
    setSelectedRepo(repo)
    setActivityDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setActivityDialogOpen(false)
    setSelectedRepo(null)
  }

  // 检查仓库是否已经被跟踪
  const isRepoTracked = (repoFullName: string) => {
    return trackedRepos.some(repo => repo.full_name === repoFullName)
  }

  // 计算有更新的仓库数量
  const getUpdatedReposCount = () => {
    return trackedRepos.filter(repo => repo.has_updates).length
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          GitHub 项目追踪器
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="项目追踪标签页">
            <Tab label="热门项目" />
            <Tab 
              label={
                getUpdatedReposCount() > 0 ? (
                  <Badge badgeContent={getUpdatedReposCount()} color="error">
                    已追踪项目
                  </Badge>
                ) : "已追踪项目"
              } 
            />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 4 }}>
            <Button 
              variant="contained" 
              onClick={handleRefreshRepos}
              disabled={loading || isLoadingHotRepos}
              sx={{ mr: 2 }}
            >
              {(loading || isLoadingHotRepos) ? <CircularProgress size={24} color="inherit" /> : '刷新热门项目'}
            </Button>
          </Box>

          <TableContainer component={Paper}>
            {isLoadingHotRepos ? (
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
                  {hotRepos.map((repo: Repo) => (
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
                          color={isRepoTracked(repo.full_name) ? "success" : "primary"}
                          onClick={() => handleTrackRepo(repo.full_name)}
                          disabled={trackMutation.isPending || isRepoTracked(repo.full_name)}
                        >
                          {trackMutation.isPending ? '跟踪中...' : isRepoTracked(repo.full_name) ? '已跟踪' : '跟踪'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            已跟踪项目列表
          </Typography>

          {isLoadingTrackedRepos ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <CircularProgress />
              <Typography sx={{ mt: 2 }}>正在加载已跟踪项目...</Typography>
            </Box>
          ) : trackedRepos.length === 0 ? (
            <Alert severity="info">
              您还没有跟踪任何项目。请在"热门项目"标签页中选择要跟踪的项目。
            </Alert>
          ) : (
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 650 }} aria-label="已跟踪项目表格">
                <TableHead>
                  <TableRow>
                    <TableCell>项目名称</TableCell>
                    <TableCell>上次更新时间</TableCell>
                    <TableCell>状态</TableCell>
                    <TableCell>操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trackedRepos.map((repo: TrackedRepo) => (
                    <TableRow key={repo.full_name}>
                      <TableCell component="th" scope="row">
                        <Typography variant="body2" component="div">
                          <strong>{repo.name || repo.full_name.split('/')[1]}</strong>
                          <br />
                          <small>{repo.full_name}</small>
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {repo.last_updated ? new Date(repo.last_updated).toLocaleString() : '尚未获取'}
                      </TableCell>
                      <TableCell>
                        {repo.has_updates ? (
                          <Alert severity="info" sx={{ py: 0 }}>有新动态</Alert>
                        ) : '无更新'}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button 
                            variant="outlined" 
                            size="small"
                            color="primary"
                            onClick={() => handleShowActivities(repo)}
                          >
                            查看动态
                          </Button>
                          <Button 
                            variant="outlined" 
                            size="small"
                            color="error"
                            onClick={() => handleUntrackRepo(repo.full_name)}
                            disabled={untrackMutation.isPending}
                          >
                            {untrackMutation.isPending ? '取消中...' : '取消跟踪'}
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>
      </Box>

      {/* 活动详情对话框 */}
      <Dialog
        open={activityDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedRepo?.name || selectedRepo?.full_name} 的最新动态
        </DialogTitle>
        <DialogContent dividers>
          {selectedRepo?.activities?.length ? (
            <List>
              {selectedRepo.activities.map((activity, index) => (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start">
                    <ListItemText
                      primary={`${activity.type}: ${activity.title}`}
                      secondary={
                        <>
                          <Typography
                            component="span"
                            variant="body2"
                            color="text.primary"
                          >
                            {new Date(activity.created_at).toLocaleString()}
                          </Typography>
                          {activity.description && ` — ${activity.description}`}
                        </>
                      }
                    />
                  </ListItem>
                  {index < selectedRepo.activities.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Typography>暂无动态</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>关闭</Button>
        </DialogActions>
      </Dialog>

      {/* 消息通知 */}
      <Snackbar
        open={!!message}
        autoHideDuration={3000}
        onClose={() => setMessage('')}
      >
        <Alert 
          severity={message.includes('成功') || message.includes('已') ? 'success' : 'error'} 
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

import React from 'react';
import { useState } from 'react';
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
  Divider,
  TextField,
  MenuItem,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormGroup,
  InputLabel,
  Select,
  SelectChangeEvent,
  Tooltip
} from '@mui/material'
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query'
import { fetchHotRepos, trackRepo, fetchTrackedRepos, untrackRepo, refreshActivities, refreshRepoActivities, searchRepos, fetchScheduledTasks, createScheduledTask, deleteScheduledTask, updateScheduledTask, executeScheduledTask } from './api/github'
import { Repo, TrackedRepo, ScheduledTask } from './types'

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
  const [loadingActivities, setLoadingActivities] = useState(false)
  const [newRepoFullName, setNewRepoFullName] = useState('')
  const [refreshDays, setRefreshDays] = useState<number>(1);
  const [refreshingRepos, setRefreshingRepos] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Repo[]>([])
  const [emailAddress, setEmailAddress] = useState('')
  const [updateFrequency, setUpdateFrequency] = useState('daily')
  const [weekday, setWeekday] = useState('1')
  const [monthDay, setMonthDay] = useState('1')
  const [scheduledRepos, setScheduledRepos] = useState<string[]>([])
  const [isSubmittingSchedule, setIsSubmittingSchedule] = useState(false)
  const [scheduledTasks, setScheduledTasks] = useState<ScheduledTask[]>([])
  const [isDeletingSchedule, setIsDeletingSchedule] = useState<string | null>(null)
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null)
  const [executeTime, setExecuteTime] = useState('09:00')

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
    queryKey: ['trackedRepos', refreshDays],
    queryFn: () => fetchTrackedRepos(refreshDays),
    enabled: true,
    refetchOnWindowFocus: false
  })

  // 获取定时任务列表的查询
  const { 
    data: scheduledTasksData = [], 
    refetch: refetchScheduledTasks,
    isLoading: isLoadingScheduledTasks 
  } = useQuery({
    queryKey: ['scheduledTasks'],
    queryFn: fetchScheduledTasks,
    enabled: true,
    refetchOnWindowFocus: false,
  });

  // 当定时任务数据变化时更新状态
  React.useEffect(() => {
    console.log('获取到的定时任务数据:', scheduledTasksData);
    setScheduledTasks(scheduledTasksData as ScheduledTask[]);
  }, [scheduledTasksData]);

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
    
    // 当切换到定时任务配置标签页时，刷新任务列表
    if (newValue === 2) {
      refetchScheduledTasks();
    }
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

  // 更新活动的处理函数
  const handleRefreshActivities = async () => {
    setLoadingActivities(true)
    try {
      await refreshActivities(refreshDays);
      refetchTrackedRepos();
      setMessage(`已刷新近 ${refreshDays} 天的活动！`);
    } catch (error) {
      console.error('刷新活动时出错:', error);
      setMessage('刷新失败，请重试');
    } finally {
      setLoadingActivities(false)
    }
  };

  const handleAddRepo = async () => {
    if (!newRepoFullName) {
      setMessage('请输入项目全名');
      return;
    }

    try {
      await trackRepo(newRepoFullName); 
      setMessage('项目已成功添加到追踪列表！');
      setNewRepoFullName(''); 
      refetchTrackedRepos(); 
    } catch (error) {
      console.error('添加项目时出错:', error);
      setMessage('添加项目失败，请检查项目名称');
    }
  };

  const handleRefreshRepoActivities = async (repoFullName: string) => {
    setRefreshingRepos(prev => new Set(prev).add(repoFullName));
    try {
      await refreshRepoActivities(repoFullName, refreshDays);
      await refetchTrackedRepos();
      setMessage(`已刷新 ${repoFullName} 近 ${refreshDays} 天的活动！`);
    } catch (error) {
      console.error('刷新仓库活动时出错:', error);
      setMessage(`刷新 ${repoFullName} 失败，请重试`);
    } finally {
      setRefreshingRepos(prev => {
        const next = new Set(prev);
        next.delete(repoFullName);
        return next;
      });
    }
  };

  // 添加搜索处理函数
  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    
    if (query.trim().length >= 3) {  // 至少3个字符才触发搜索
      setIsSearching(true)
      try {
        const results = await searchRepos(query)
        setSearchResults(results)
      } catch (error) {
        console.error('搜索出错:', error)
        setMessage('搜索失败，请重试')
      } finally {
        setIsSearching(false)
      }
    } else {
      setSearchResults([])
    }
  }

  // 修改过滤逻辑
  const displayedRepos = searchQuery.length >= 3 ? searchResults : hotRepos
  const filteredRepos = displayedRepos.filter(repo => 
    repo.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    repo.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleSaveSchedule = async () => {
    setIsSubmittingSchedule(true)
    try {
      const taskData = {
        email: emailAddress,
        repositories: scheduledRepos,
        frequency: updateFrequency,
        ...(updateFrequency === 'weekly' ? { weekday } : {}),
        ...(updateFrequency === 'monthly' ? { monthDay } : {}),
        executeTime: executeTime
      };
      
      if (editingTaskId) {
        // 更新现有任务
        await updateScheduledTask(editingTaskId, taskData);
        setMessage('定时任务配置已更新！');
      } else {
        // 创建新任务
        await createScheduledTask(taskData);
        setMessage('定时任务配置已保存！');
      }
      
      // 强制刷新任务列表
      await refetchScheduledTasks();
      
      // 清空表单
      setEditingTaskId(null);
      setEmailAddress('');
      setScheduledRepos([]);
      setUpdateFrequency('daily');
      setWeekday('1');
      setMonthDay('1');
      setExecuteTime('09:00');
    } catch (error) {
      console.error('保存配置时出错:', error)
      setMessage(editingTaskId ? '更新配置失败，请重试' : '保存配置失败，请重试')
    } finally {
      setIsSubmittingSchedule(false)
    }
  }

  const handleDeleteSchedule = async (id: string) => {
    setIsDeletingSchedule(id)
    try {
      await deleteScheduledTask(id);
      setMessage('定时任务已删除！');
      
      // 强制刷新任务列表
      await refetchScheduledTasks();
    } catch (error) {
      console.error('删除定时任务时出错:', error)
      setMessage('删除定时任务失败，请重试')
    } finally {
      setIsDeletingSchedule(null)
    }
  }

  const getScheduleDescription = (task: ScheduledTask) => {
    const time = task.executeTime || '09:00';
    
    switch(task.frequency) {
      case 'immediate':
        return '立即执行（一次性）';
      case 'daily':
        return `每天 ${time}`;
      case 'weekly':
        return `每周${['一', '二', '三', '四', '五', '六', '日'][parseInt(task.weekday || '1') - 1]} ${time}`;
      case 'monthly':
        return `每月${task.monthDay}日 ${time}`;
      default:
        return task.frequency;
    }
  }

  const handleEditTask = (task: ScheduledTask) => {
    setEditingTaskId(task.id);
    setEmailAddress(task.email);
    setScheduledRepos(task.repositories);
    setUpdateFrequency(task.frequency);
    if (task.frequency === 'weekly') {
      setWeekday(task.weekday || '1');
    } else if (task.frequency === 'monthly') {
      setMonthDay(task.monthDay || '1');
    }
    setExecuteTime(task.executeTime || '09:00');
  }

  const handleExecuteNow = async (id: string) => {
    try {
      // 调用后端API执行任务
      await executeScheduledTask(id);
      setMessage('定时任务已执行！');
    } catch (error) {
      console.error('执行定时任务时出错:', error);
      setMessage('执行定时任务失败，请重试');
    }
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
            <Tab label="定时任务配置" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 4, display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button 
              variant="contained" 
              onClick={handleRefreshRepos}
              disabled={loading || isLoadingHotRepos}
            >
              {(loading || isLoadingHotRepos) ? <CircularProgress size={24} color="inherit" /> : '刷新热门项目'}
            </Button>
            
            {/* 添加搜索框 */}
            <TextField
              label="搜索项目"
              variant="outlined"
              size="small"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              sx={{ flexGrow: 1 }}
              placeholder="输入至少3个字符搜索项目..."
            />
          </Box>

          <TableContainer component={Paper}>
            {(isLoadingHotRepos || isSearching) ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <CircularProgress />
                <Typography sx={{ mt: 2 }}>
                  {isSearching ? '正在搜索项目...' : '正在加载项目数据...'}
                </Typography>
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
                    <TableCell>GitHub</TableCell>
                    <TableCell>操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredRepos.map((repo: Repo) => (
                    <TableRow key={repo.full_name}>
                      <TableCell component="th" scope="row">
                        <Typography variant="body2" component="div">
                          <strong>{repo.name}</strong>
                          <br />
                          <small>{repo.full_name}</small>
                        </Typography>
                      </TableCell>
                      <TableCell component="th" scope="row">
                        <Typography variant="body2" component="div">
                          <strong>{repo.description_zh}</strong>
                          <br />
                          <small>{repo.description}</small>
                        </Typography>
                      </TableCell>
                      <TableCell align="right">{repo.stars}</TableCell>
                      <TableCell align="right">{repo.forks}</TableCell>
                      <TableCell align="right">
                        {new Date(repo.updated_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="text"
                          size="small"
                          href={`https://github.com/${repo.full_name}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          访问
                        </Button>
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

          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            {/* 添加项目输入框 */}
            <TextField
              label="输入项目全名 (例如: owner/repo)"
              variant="outlined"
              value={newRepoFullName}
              onChange={(e) => setNewRepoFullName(e.target.value)}
              sx={{ flexGrow: 1 }}
            />
            <Button 
              variant="contained" 
              onClick={handleAddRepo}
              disabled={!newRepoFullName}
            >
              添加项目
            </Button>
            
            {/* 时间范围选择 */}
            <TextField
              select
              label="刷新时间范围"
              value={refreshDays}
              onChange={(e) => setRefreshDays(Number(e.target.value))}
              sx={{ width: 150 }}
            >
              <MenuItem value={1}>近1天</MenuItem>
              <MenuItem value={7}>近1周</MenuItem>
              <MenuItem value={30}>近1月</MenuItem>
              <MenuItem value={90}>近3月</MenuItem>
            </TextField>
            
            {/* 刷新活动按钮 */}
            <Button 
              variant="outlined" 
              onClick={handleRefreshActivities} 
              disabled={loadingActivities}
            >
              {loadingActivities ? 
                <CircularProgress size={24} color="inherit" /> : 
                `刷新近${refreshDays}天活动`
              }
            </Button>
          </Box>

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
              <Table sx={{ minWidth: 650 }} aria-label="已追踪项目表格">
                <TableHead>
                  <TableRow>
                    <TableCell>项目名称</TableCell>
                    <TableCell>描述</TableCell>
                    <TableCell align="right">Stars</TableCell>
                    <TableCell align="right">Forks</TableCell>
                    <TableCell align="right">最近更新</TableCell>
                    <TableCell>GitHub</TableCell>
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
                      <TableCell component="th" scope="row">
                        <Typography variant="body2" component="div">
                          <strong>{repo.description}</strong>
                        </Typography>
                      </TableCell>
                      <TableCell align="right">{repo.stars}</TableCell>
                      <TableCell align="right">{repo.forks}</TableCell>
                      <TableCell align="right">
                        {repo.last_updated ? new Date(repo.last_updated).toLocaleString() : '尚未获取'}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="text"
                          size="small"
                          href={`https://github.com/${repo.full_name}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          访问
                        </Button>
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
                            color="info"
                            onClick={() => handleRefreshRepoActivities(repo.full_name)}
                            disabled={refreshingRepos.has(repo.full_name)}
                          >
                            {refreshingRepos.has(repo.full_name) ? (
                              <CircularProgress size={20} color="inherit" />
                            ) : (
                              `刷新`
                            )}
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

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            定时任务配置
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            您可以配置定时任务，系统将自动检查项目更新并发送邮件通知。
          </Typography>

          <Box sx={{ 
            display: 'flex', 
            gap: 3, 
            flexDirection: { xs: 'column', md: 'row' },
            height: 'calc(100vh - 250px)',
            overflow: 'hidden'
          }}>
            {/* 左侧配置表单 */}
            <Paper sx={{ p: 3, flex: 1, overflow: 'auto' }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                邮件通知设置
              </Typography>
              
              <TextField
                label="接收邮箱"
                variant="outlined"
                fullWidth
                margin="normal"
                placeholder="example@example.com"
                value={emailAddress || ''}
                onChange={(e) => setEmailAddress(e.target.value)}
                sx={{ mb: 2 }}
              />
              
              <Typography variant="subtitle1" gutterBottom fontWeight="bold" sx={{ mt: 2 }}>
                更新频率
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                <FormControl component="fieldset">
                  <RadioGroup
                    value={updateFrequency}
                    onChange={(e) => setUpdateFrequency(e.target.value)}
                  >
                    <FormControlLabel value="immediate" control={<Radio />} label="立即执行" />
                    <FormControlLabel value="daily" control={<Radio />} label="每天" />
                    <FormControlLabel value="weekly" control={<Radio />} label="每周" />
                    <FormControlLabel value="monthly" control={<Radio />} label="每月" />
                  </RadioGroup>
                </FormControl>

                {updateFrequency === 'daily' && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography>时间：</Typography>
                    <TextField
                      type="time"
                      value={executeTime}
                      onChange={(e) => setExecuteTime(e.target.value)}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      inputProps={{
                        step: 300, // 5分钟间隔
                      }}
                      sx={{ width: 150 }}
                    />
                  </Box>
                )}
                
                {updateFrequency === 'weekly' && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>星期几</InputLabel>
                      <Select
                        value={weekday}
                        onChange={(e: SelectChangeEvent) => setWeekday(e.target.value)}
                        label="星期几"
                      >
                        <MenuItem value="1">星期一</MenuItem>
                        <MenuItem value="2">星期二</MenuItem>
                        <MenuItem value="3">星期三</MenuItem>
                        <MenuItem value="4">星期四</MenuItem>
                        <MenuItem value="5">星期五</MenuItem>
                        <MenuItem value="6">星期六</MenuItem>
                        <MenuItem value="7">星期日</MenuItem>
                      </Select>
                    </FormControl>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography>时间：</Typography>
                      <TextField
                        type="time"
                        value={executeTime}
                        onChange={(e) => setExecuteTime(e.target.value)}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        inputProps={{
                          step: 300, // 5分钟间隔
                        }}
                        sx={{ width: 150 }}
                      />
                    </Box>
                  </Box>
                )}
                
                {updateFrequency === 'monthly' && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>日期</InputLabel>
                      <Select
                        value={monthDay}
                        onChange={(e: SelectChangeEvent) => setMonthDay(e.target.value)}
                        label="日期"
                      >
                        {Array.from({ length: 28 }, (_, i) => (
                          <MenuItem key={i + 1} value={(i + 1).toString()}>
                            {i + 1} 日
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography>时间：</Typography>
                      <TextField
                        type="time"
                        value={executeTime}
                        onChange={(e) => setExecuteTime(e.target.value)}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        inputProps={{
                          step: 300, // 5分钟间隔
                        }}
                        sx={{ width: 150 }}
                      />
                    </Box>
                  </Box>
                )}
              </Box>
              
              <Typography variant="subtitle1" gutterBottom fontWeight="bold" sx={{ mt: 2 }}>
                选择要监控的项目
              </Typography>
              
              {trackedRepos.length === 0 ? (
                <Alert severity="info" sx={{ mb: 2 }}>
                  您还没有跟踪任何项目。请先在"已追踪项目"标签页中添加项目。
                </Alert>
              ) : (
                <Box sx={{ maxHeight: '300px', overflowY: 'auto', mb: 2 }}>
                  <FormGroup>
                    {trackedRepos.map((repo) => (
                      <FormControlLabel
                        key={repo.full_name}
                        control={
                          <Checkbox
                            checked={scheduledRepos.includes(repo.full_name)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setScheduledRepos([...scheduledRepos, repo.full_name]);
                              } else {
                                setScheduledRepos(
                                  scheduledRepos.filter((name) => name !== repo.full_name)
                                );
                              }
                            }}
                          />
                        }
                        label={`${repo.name} (${repo.full_name})`}
                      />
                    ))}
                  </FormGroup>
                </Box>
              )}
              
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                {editingTaskId && (
                  <Button
                    variant="outlined"
                    color="secondary"
                    onClick={() => {
                      // 取消编辑
                      setEditingTaskId(null);
                      setEmailAddress('');
                      setScheduledRepos([]);
                      setUpdateFrequency('daily');
                      setWeekday('1');
                      setMonthDay('1');
                      setExecuteTime('09:00');
                    }}
                  >
                    取消
                  </Button>
                )}
                <Button 
                  variant="contained" 
                  color="primary"
                  disabled={!emailAddress || scheduledRepos.length === 0 || isSubmittingSchedule}
                  onClick={handleSaveSchedule}
                >
                  {isSubmittingSchedule ? 
                    <CircularProgress size={24} color="inherit" /> : 
                    editingTaskId ? '更新配置' : '保存配置'
                  }
                </Button>
              </Box>
            </Paper>

            {/* 右侧任务列表 */}
            <Paper sx={{ p: 3, flex: 1, overflow: 'auto' }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                已配置的定时任务
              </Typography>
              
              {isLoadingScheduledTasks ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : scheduledTasks.length === 0 ? (
                <Alert severity="info" sx={{ mb: 2 }}>
                  暂无已配置的定时任务
                </Alert>
              ) : (
                <TableContainer sx={{ maxHeight: 'calc(100vh - 300px)', overflowY: 'auto' }}>
                  <Table size="small" stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>邮箱</TableCell>
                        <TableCell>监控项目</TableCell>
                        <TableCell>更新频率</TableCell>
                        <TableCell>操作</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {scheduledTasks.map((task) => (
                        <TableRow key={task.id}>
                          <TableCell>{task.email}</TableCell>
                          <TableCell>
                            <Tooltip title={task.repositories.map(repoName => {
                              const repo = trackedRepos.find(r => r.full_name === repoName);
                              return repo ? repo.name : repoName;
                            }).join(', ')}>
                              <Typography noWrap sx={{ maxWidth: '150px' }}>
                                {task.repositories.map(repoName => {
                                  const repo = trackedRepos.find(r => r.full_name === repoName);
                                  return repo ? repo.name : repoName;
                                }).join(', ')}
                              </Typography>
                            </Tooltip>
                          </TableCell>
                          <TableCell>{getScheduleDescription(task)}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Button
                                color="primary"
                                size="small"
                                onClick={() => handleEditTask(task)}
                                disabled={isSubmittingSchedule || isDeletingSchedule !== null}
                              >
                                编辑
                              </Button>
                              <Button
                                color="error"
                                size="small"
                                onClick={() => handleDeleteSchedule(task.id)}
                                disabled={isSubmittingSchedule || isDeletingSchedule !== null}
                              >
                                {isDeletingSchedule === task.id ? <CircularProgress size={20} /> : '删除'}
                              </Button>
                              {task.frequency === 'immediate' ? (
                                <Button
                                  color="info"
                                  size="small"
                                  onClick={() => handleExecuteNow(task.id)}
                                  disabled={isSubmittingSchedule || isDeletingSchedule !== null}
                                >
                                  再次执行
                                </Button>
                              ) : (
                                <Button
                                  color="info"
                                  size="small"
                                  onClick={() => handleExecuteNow(task.id)}
                                  disabled={isSubmittingSchedule || isDeletingSchedule !== null}
                                >
                                  立即执行
                                </Button>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Box>
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

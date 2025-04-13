import { useState } from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Snackbar,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchTrackedRepos, untrackRepo } from '../api/github'
import { TrackedRepo } from '../types'

export default function TrackedRepoList() {
  const [message, setMessage] = useState('')
  const queryClient = useQueryClient()

  const { data: repos = [], isLoading } = useQuery({
    queryKey: ['trackedRepos'],
    queryFn: fetchTrackedRepos
  })

  const untrackMutation = useMutation({
    mutationFn: untrackRepo,
    onSuccess: () => {
      setMessage('已取消追踪')
      queryClient.invalidateQueries({ queryKey: ['trackedRepos'] })
    },
    onError: () => {
      setMessage('操作失败，请重试')
    }
  })

  if (isLoading) {
    return <Typography>加载中...</Typography>
  }

  return (
    <>
      <Grid container spacing={2}>
        {repos.map((repo: TrackedRepo) => (
          <Grid item xs={12} key={repo.full_name}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div" gutterBottom>
                  {repo.name}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  {repo.full_name}
                </Typography>
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>最新动态</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {repo.activities?.length > 0 ? (
                      repo.activities.map((activity, index) => (
                        <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                          • {activity.type}: {activity.title}
                          <br />
                          <small>{new Date(activity.created_at).toLocaleString()}</small>
                        </Typography>
                      ))
                    ) : (
                      <Typography variant="body2">暂无动态</Typography>
                    )}
                  </AccordionDetails>
                </Accordion>

                <Button 
                  variant="outlined" 
                  color="error"
                  size="small" 
                  sx={{ mt: 2 }}
                  onClick={() => untrackMutation.mutate(repo.full_name)}
                >
                  取消追踪
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Snackbar
        open={!!message}
        autoHideDuration={3000}
        onClose={() => setMessage('')}
      >
        <Alert severity="info" onClose={() => setMessage('')}>
          {message}
        </Alert>
      </Snackbar>
    </>
  )
} 
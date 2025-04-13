import { useState } from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Snackbar,
  Alert
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchHotRepos, trackRepo } from '../api/github'
import { Repo } from '../types'

export default function RepoList() {
  const [message, setMessage] = useState('')
  const queryClient = useQueryClient()

  const { data: repos = [], isLoading } = useQuery({
    queryKey: ['hotRepos'],
    queryFn: fetchHotRepos
  })

  const trackMutation = useMutation({
    mutationFn: trackRepo,
    onSuccess: () => {
      setMessage('项目追踪成功！')
      queryClient.invalidateQueries({ queryKey: ['trackedRepos'] })
    },
    onError: () => {
      setMessage('追踪失败，请重试')
    }
  })

  if (isLoading) {
    return <Typography>加载中...</Typography>
  }

  return (
    <>
      <Grid container spacing={2}>
        {repos.map((repo: Repo) => (
          <Grid item xs={12} sm={6} md={4} key={repo.full_name}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div" gutterBottom>
                  {repo.name}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  {repo.full_name}
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {repo.description}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ⭐ {repo.stars} · 🔄 {repo.forks}
                </Typography>
                <Button 
                  variant="outlined" 
                  size="small" 
                  sx={{ mt: 1 }}
                  onClick={() => trackMutation.mutate(repo.full_name)}
                >
                  追踪
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
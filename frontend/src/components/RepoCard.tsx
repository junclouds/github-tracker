import React, { useState } from 'react';
import {
    Card,
    CardContent,
    CardActions,
    Typography,
    Button,
    Box,
    Chip,
    Stack
} from '@mui/material';
import { Repo } from '../types';
import { ActivityDialog } from './ActivityDialog';

interface RepoCardProps {
    repo: Repo;
    isTracked?: boolean;
    onTrack?: (repo: Repo) => void;
}

export const RepoCard: React.FC<RepoCardProps> = ({ repo, isTracked = false, onTrack }) => {
    const [dialogOpen, setDialogOpen] = useState(false);

    const handleTrack = () => {
        onTrack?.(repo);
    };

    return (
        <>
            <Card variant="outlined">
                <CardContent>
                    <Typography variant="h6" component="div" gutterBottom>
                        {repo.name}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        {repo.full_name}
                    </Typography>

                    {repo.description && (
                        <Box sx={{ mb: 2 }}>
                            <Typography variant="body1" paragraph>
                                {repo.description}
                            </Typography>
                            {repo.description_zh && (
                                <Typography variant="body2" color="text.secondary">
                                    {repo.description_zh}
                                </Typography>
                            )}
                        </Box>
                    )}

                    <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                        <Chip label={`⭐ ${repo.stars}`} size="small" />
                        <Chip label={`🍴 ${repo.forks}`} size="small" />
                    </Stack>

                    <Typography variant="caption" color="text.secondary">
                        最后更新: {new Date(repo.updated_at).toLocaleString()}
                    </Typography>
                </CardContent>

                <CardActions>
                    <Button
                        size="small"
                        href={repo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        访问GitHub
                    </Button>
                    {onTrack && (
                        <Button
                            size="small"
                            onClick={handleTrack}
                            disabled={isTracked}
                        >
                            {isTracked ? '已跟踪' : '跟踪'}
                        </Button>
                    )}
                    {isTracked && (
                        <Button
                            size="small"
                            onClick={() => setDialogOpen(true)}
                        >
                            查看动态
                        </Button>
                    )}
                </CardActions>
            </Card>

            <ActivityDialog
                repo={repo}
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
            />
        </>
    );
}; 
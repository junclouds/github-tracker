import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    List,
    ListItem,
    ListItemText,
    Typography,
    Divider,
    Box,
    Paper
} from '@mui/material';
import { TrackedRepo, Activity } from '../types';

interface ActivityDialogProps {
    repo: TrackedRepo | null;
    open: boolean;
    onClose: () => void;
}

export const ActivityDialog: React.FC<ActivityDialogProps> = ({ repo, open, onClose }) => {
    if (!repo) return null;

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
        >
            <DialogTitle>
                {repo.name} 的最新动态
            </DialogTitle>
            
            {repo.summary && (
                <Box sx={{ px: 3, py: 2 }}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Typography variant="h6" gutterBottom>
                            活动总结
                        </Typography>
                        <Typography variant="body1">
                            {repo.summary}
                        </Typography>
                    </Paper>
                </Box>
            )}
            
            <DialogContent dividers>
                {repo.activities?.length ? (
                    <List>
                        {repo.activities.map((activity, index) => (
                            <React.Fragment key={index}>
                                <ListItem alignItems="flex-start">
                                    <ListItemText
                                        primary={
                                            <Box sx={{ mb: 1 }}>
                                                <Typography variant="subtitle1">
                                                    {activity.type}: {activity.title}
                                                </Typography>
                                                {activity.title_zh && (
                                                    <Typography variant="body2" color="text.secondary">
                                                        {activity.title_zh}
                                                    </Typography>
                                                )}
                                            </Box>
                                        }
                                        secondary={
                                            <>
                                                <Typography component="span" variant="body2" color="text.primary">
                                                    {new Date(activity.created_at).toLocaleString()}
                                                </Typography>
                                                {activity.description && (
                                                    <Box sx={{ mt: 1 }}>
                                                        <Typography variant="body2">
                                                            {activity.description}
                                                        </Typography>
                                                        {activity.description_zh && (
                                                            <Typography variant="body2" color="text.secondary">
                                                                {activity.description_zh}
                                                            </Typography>
                                                        )}
                                                    </Box>
                                                )}
                                                {activity.url && (
                                                    <Button
                                                        href={activity.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        size="small"
                                                        sx={{ mt: 1 }}
                                                    >
                                                        查看详情
                                                    </Button>
                                                )}
                                            </>
                                        }
                                    />
                                </ListItem>
                                {index < repo.activities.length - 1 && <Divider />}
                            </React.Fragment>
                        ))}
                    </List>
                ) : (
                    <Typography>暂无动态</Typography>
                )}
            </DialogContent>
            
            <DialogActions>
                <Button onClick={onClose}>关闭</Button>
                <Button
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    color="primary"
                >
                    访问GitHub
                </Button>
            </DialogActions>
        </Dialog>
    );
}; 
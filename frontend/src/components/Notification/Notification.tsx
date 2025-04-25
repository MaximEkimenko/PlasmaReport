import React from "react";
import { IconButton, Snackbar } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

type NotificationProps = {message?: string, value: boolean, setValue: React.Dispatch<React.SetStateAction<boolean>>}

const Notification = ({message="Записи обновлены", value, setValue}:NotificationProps) => {
    const handleCloseNotification = () => setValue(false);

    return (
        <Snackbar
            message={message}
            open={value}
            autoHideDuration={3000}
            onClose={handleCloseNotification}
            action={
                <IconButton aria-label="close" color="inherit" sx={{ p: 0.5 }} onClick={handleCloseNotification}>
                    <CloseIcon />
                </IconButton>
            }
        />
    );
};

export default Notification;

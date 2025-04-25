import { Box, Modal, Fade, Backdrop } from "@mui/material";
import { useState } from "react";
import CloseIcon from '@mui/icons-material/Close';


type ImageWidgetProps = { source: string | null };
export function ImageWidget({ source }: ImageWidgetProps) {
    const [openModal, setOpenModal] = useState(false)
    return (
        <>
        {source === null && 
        <Box sx = {{display:"flex",  justifyContent:"center", width:"100%", height:"100%", alignItems:"center"}}>
            <CloseIcon sx={{color:"error.main"}}/>
        </Box>}
            {source !== null && (
                <>
            <Box
                component="img"
                src={source}
                alt="preview"
                sx={{
                    p:0,
                    height: 110,
                    //width: "auto",
                    maxWidth: "100%",
                    objectFit: "cover",
                    cursor: "pointer",
                }}
                onClick={()=>setOpenModal(true)}
            />

            <Modal
                open={openModal}
                onClose={()=>setOpenModal(false)}
                closeAfterTransition
                slots={{ backdrop: Backdrop }}
                slotProps={{
                    backdrop: {
                        timeout: 300,
                    },
                }}
            >
                <Fade in={openModal}>
                    <Box
                        sx={{
                            position: "absolute",
                            top: "50%",
                            left: "50%",
                            transform: "translate(-50%, -50%)",
                            maxWidth: "90vw",
                            maxHeight: "90vh",
                            outline: "none",
                            p: 2,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            backgroundColor: "transparent",
                            
                        }}
                    >
                        <Box
                            component="img"
                            src={source ?? ""}
                            alt="full preview"
                            sx={{
                                maxWidth: "none",
                                maxHeight: "none",
                                borderRadius: 2,
                                boxShadow: 5,
                                backgroundColor: "#fff",
                            }}
                            onClick={()=>setOpenModal(false)} 
                        />
                    </Box>
                </Fade>
            </Modal>
            </>
            )
}
        </>
    );
}

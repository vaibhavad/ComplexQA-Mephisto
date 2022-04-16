import React from "react";
import { Button, Modal } from "react-bootstrap";


function SameAnswerModal({ showSameAnswerModal, setShowSameAnswerModal, currentAnswer, currentQuestion }) {

    const handleClose = () => setShowSameAnswerModal(false);

    return (
        <Modal show={showSameAnswerModal} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>Does the question have the same answer as the latest conversational answer?</Modal.Title>
            </Modal.Header>
            <Modal.Body>Please ensure that for the question: <b>{currentQuestion}</b>, the answer is <b>{currentAnswer}</b>. </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

export { SameAnswerModal };
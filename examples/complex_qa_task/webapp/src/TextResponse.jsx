/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { FormControl, Button } from "react-bootstrap";

const BOOL_MESSAGE = "It it possible to form complex question from the most recent QA pair?"
const BOOL_MORE_QUESTIONS_MESSAGE = "It is possible to form another complex question?"
const TEXT_INPUT_MESSAGE = "Please provide the complex question below"
const MAX_QUESTIONS_PER_TURN = 3
const MOVE_TO_NEXT_TURN_MESSAGE = "Only " + MAX_QUESTIONS_PER_TURN + " complex questions allowed per turn. Please move to the next turn."
const SAME_ANSWER_MODEL_PROB = 0.3

function TextResponse({ onMessageSend, active, boolResponse, boolResponseProvideMoreQuestions, amountEarned, setAmountEarned, taskConfig, setCurrentQuestion, setShowSameAnswerModal, firstQuestionProvided, setFirstQuestionProvided, doNotDisturb }) {

  const [textValue, setTextValue] = React.useState("");
  const [sending, setSending] = React.useState(false);
  const [numComplexPerTurn, setNumComplexPerTurn] = React.useState(0);
  const [shownSameAnswerModalOnce, setShownSameAnswerModalOnce] = React.useState(false);

  const inputRef = React.useRef();

  React.useEffect(() => {
    if (active && inputRef.current && inputRef.current.focus) {
      inputRef.current.focus();
    }
  }, [active]);

  const tryMessageSend = React.useCallback(() => {
    setCurrentQuestion(textValue);
    if ((!firstQuestionProvided || Math.random() < SAME_ANSWER_MODEL_PROB) && !shownSameAnswerModalOnce && !doNotDisturb) {
      setShownSameAnswerModalOnce(true);
      setShowSameAnswerModal(true);
    }
    else if (textValue !== "" && active && !sending) {
      setSending(true);
      onMessageSend({ text: textValue, task_data: {} }).then(() => {
        setTextValue("");
        setSending(false);
        setAmountEarned(amountEarned + taskConfig.task_reward_question);
        setNumComplexPerTurn(numComplexPerTurn + 1);
        setShownSameAnswerModalOnce(false);
        setFirstQuestionProvided(true);
      });
    }
  }, [textValue, active, sending, onMessageSend, shownSameAnswerModalOnce, firstQuestionProvided, doNotDisturb]);

  const tryBoolMessageSend = React.useCallback((boolValue) => {
    if (active && !sending) {
      setSending(true);
      onMessageSend({ boolValue: boolValue, task_data: {} }).then(() => {
        setSending(false);
        setAmountEarned(amountEarned + taskConfig.task_reward_bool);
      });
    }
  }, [active, sending, onMessageSend]);

  const tryBoolMessageProvideMoreQuestions = React.useCallback((boolValue) => {
    if (!boolValue) {
      setNumComplexPerTurn(0);
    }
    if (active && !sending) {
      setSending(true);
      onMessageSend({ boolValueProvideMoreQuestions: boolValue, task_data: {} }).then(() => {
        setSending(false);
      });
    }
  }, [active, sending, onMessageSend]);

  const handleKeyPress = React.useCallback(
    (e) => {
      if (e.key === "Enter") {
        tryMessageSend();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
      }
    },
    [tryMessageSend]
  );

  if (boolResponse) {
    return (
      <div className="response-type-module">
        <div className="response-type-module-instruction">
          <p><b>{BOOL_MESSAGE}</b></p>
        </div>
        <div className="response-bar">
          <Button
            className="btn btn-primary btn-bool btn-yes"
            disabled={!active || sending}
            onClick={() => tryBoolMessageSend(true)}
          ><span className="glyphicon glyphicon-ok" aria-hidden="true" /> Yes
          </Button>
          <Button
            className="btn btn-primary btn-bool btn-no"
            disabled={!active || sending}
            onClick={() => tryBoolMessageSend(false)}
          ><span className="glyphicon glyphicon-remove" aria-hidden="true" /> No
          </Button>
        </div>
      </div>
    );

  } else if (boolResponseProvideMoreQuestions) {
    return (
      <div className="response-type-module">
        <div className="response-type-module-instruction">
          <p><b>{numComplexPerTurn < MAX_QUESTIONS_PER_TURN ? BOOL_MORE_QUESTIONS_MESSAGE : MOVE_TO_NEXT_TURN_MESSAGE}</b></p>
        </div>
        <div className="response-bar">
          {numComplexPerTurn < MAX_QUESTIONS_PER_TURN ? <Button
            className="btn btn-primary btn-bool"
            disabled={!active || sending}
            onClick={() => tryBoolMessageProvideMoreQuestions(true)}
          ><span className="glyphicon" aria-hidden="true" /> Provide another question
          </Button> : null}
          <Button
            className="btn btn-primary btn-bool"
            disabled={!active || sending}
            onClick={() => tryBoolMessageProvideMoreQuestions(false)}
          ><span className="glyphicon" aria-hidden="true" /> Move to next turn
          </Button>
        </div>
      </div>
    );

  } else {
    return (
      <div className="response-type-module">
        <div className="response-type-module-instruction">
          <p><b>{TEXT_INPUT_MESSAGE}</b></p>
        </div>
        <div className="response-bar">
          <FormControl
            type="text"
            className="response-text-input"
            inputRef={(ref) => {
              inputRef.current = ref;
            }}
            value={textValue}
            placeholder="Please enter here..."
            onKeyPress={(e) => handleKeyPress(e)}
            onChange={(e) => setTextValue(e.target.value)}
            disabled={!active || sending}
          />
          <Button
            className="btn btn-primary submit-response"
            id="id_send_msg_button"
            disabled={textValue === "" || !active || sending}
            onClick={() => tryMessageSend()}
          >
            Send
          </Button>
        </div>
      </div>
    );
  }
}

export { TextResponse };

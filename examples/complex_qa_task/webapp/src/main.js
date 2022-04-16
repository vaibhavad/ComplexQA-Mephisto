/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import "../../../../packages/bootstrap-chat/styles.css";

import { ChatApp, INPUT_MODE } from "../../../../packages/bootstrap-chat";
import { TextResponse } from "./TextResponse.jsx"
import { ProvidedQuestions } from "./ProvidedQuestions.jsx"
import { DefaultTaskDescription } from "./DefaultTaskDescription.jsx"
import { SameAnswerModal } from "./SameAnswerModal.jsx";
import ChatMessage from "./ChatMessage.jsx"

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  if ('text' in message && message.text.length > 0) {

    var messageText = message.text;
    if ('question' in message && 'answer' in message) {
      messageText = message
      return (
        <ChatMessage
          isSelf={message.id === agentId || message.id in currentAgentNames}
          agentName={
            message.id in currentAgentNames
              ? currentAgentNames[message.id]
              : message.id
          }
          message={messageText}
          taskData={message.task_data}
          messageId={message.update_id}
        />
      );
    }
  }
  return null;
}

function MainApp() {

  const [boolResponse, setBoolResponse] = React.useState(false);
  const [boolResponseProvideMoreQuestions, setBoolResponseProvideMoreQuestions] = React.useState(false);
  const [turnsRemaining, setTurnsRemaining] = React.useState(-1);
  const [providedQuestions, setProvidedQuestions] = React.useState([]);
  const [amountEarned, setAmountEarned] = React.useState(0.0);
  const [currentAnswer, setCurrentAnswer] = React.useState('');
  const [currentQuestion, setCurrentQuestion] = React.useState('');
  const [showSameAnswerModal, setShowSameAnswerModal] = React.useState(false);
  const [firstQuestionProvided, setFirstQuestionProvided] = React.useState(false);
  const [doNotDisturb, setDoNotDisturb] = React.useState(false);

  return (
    <div>
    <ChatApp
      turnsRemaining={turnsRemaining}
      setAmountEarned={setAmountEarned}
      amountEarned={amountEarned}
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.update_id + "-" + idx}
        />
      )}
      renderSidePane={({ mephistoContext: { taskConfig } }) => (
        <div>
          <DefaultTaskDescription
            chatTitle={taskConfig.chat_title}
            taskDescriptionHtml={"<div></div>"}
          >
            <p>
                In this task, you will create <b>COMPLEX</b> by combining questions from a quiz-like <b>CONVERSATION</b>.
                Remember two rules of thumb:
                <ul>
                    <li><b>COMPLEX</b> questions are questions which require you to answer two or more sub-questions in order to answer the overall question.</li>
					<li>Your <b>COMPLEX</b> questions must have the same answer as the latest question/answer pair in the <b>CONVERSATION</b>.</li>
                </ul>
				For a complete description of this task, refer to the <a href="https://shorturl.at/ejsO6">instructions</a>.

            </p>
          </DefaultTaskDescription>
          <ProvidedQuestions providedQuestions={providedQuestions} />
        </div>
      )}
      renderTextResponse={({ onMessageSend, inputMode, active, appContext, mephistoContext }) => (
        <TextResponse
          onMessageSend={onMessageSend}
          active={inputMode === INPUT_MODE.READY_FOR_INPUT || inputMode === INPUT_MODE.READY_FOR_BOOL_INPUT}
          boolResponse={boolResponse}
          boolResponseProvideMoreQuestions={boolResponseProvideMoreQuestions}
          amountEarned={amountEarned}
          setAmountEarned={setAmountEarned}
          taskConfig={mephistoContext.taskConfig}
          setCurrentQuestion={setCurrentQuestion}
          setShowSameAnswerModal={setShowSameAnswerModal}
          firstQuestionProvided={firstQuestionProvided}
          setFirstQuestionProvided={setFirstQuestionProvided}
          doNotDisturb={doNotDisturb}
        />
      )}
      onMessagesChange={(messages) => {
        if (messages && messages.length > 0) {
          const message = messages[messages.length - 1]
          if ('text' in message && message.text.trim().length > 0) {
            setProvidedQuestions(providedQuestions.concat(message.text.trim()))
          }
          if ('requires_bool_input' in message) {
            if (message.requires_bool_input) {
              setBoolResponse(true);
              if ('answer' in message) {
                setCurrentAnswer(message.answer);
              }
            } else {
              setBoolResponse(false);
            }
          }
          if ('provide_more_questions' in message) {
            if (message.provide_more_questions) {
              setBoolResponseProvideMoreQuestions(true);
            } else {
              setBoolResponseProvideMoreQuestions(false);
            }
          }
          if ('turns_remaining' in message) {
            setTurnsRemaining(message.turns_remaining);
          }
        }
      }}
    />
    <SameAnswerModal showSameAnswerModal={showSameAnswerModal} setShowSameAnswerModal={setShowSameAnswerModal} currentAnswer={currentAnswer} currentQuestion={currentQuestion} firstQuestionProvided={firstQuestionProvided} setDoNotDisturb={setDoNotDisturb} />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));

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

  return (
    <ChatApp
      turnsRemaining={turnsRemaining}
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
              task description will appear here.
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
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));

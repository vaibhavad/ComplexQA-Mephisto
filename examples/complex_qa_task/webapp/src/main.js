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

import { ChatApp, DefaultTaskDescription, INPUT_MODE } from "../../../../packages/bootstrap-chat";
import { TextResponse } from "./TextResponse.jsx"
import ChatMessage from "./ChatMessage.jsx"

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  if ('text' in message && message.text.length > 0) {

    var messageText = message.text;
    if ('question' in message && 'answer' in message) {
      messageText = message
    }

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
  return null;
}

function MainApp() {

  const [boolResponse, setBoolResponse] = React.useState(false);
  return (
    <ChatApp
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
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <h2>This is a custom Task Description loaded from a custom bundle</h2>
          <p>
            It has the ability to do a number of things, like directly access
            the contents of task data, view the number of messages so far, and
            pretty much anything you make like. We're also able to control other
            components as well, as in this example we've made it so that if you
            click a message, it will alert with that message idx.
          </p>
          <p>The regular task description content will now appear below:</p>
        </DefaultTaskDescription>
      )}
      renderTextResponse={({ onMessageSend, inputMode, active, appContext, mephistoContext }) => (
        <TextResponse
          onMessageSend={onMessageSend}
          active={inputMode === INPUT_MODE.READY_FOR_INPUT || inputMode === INPUT_MODE.READY_FOR_BOOL_INPUT}
          boolResponse={boolResponse}
        />
      )}
      onMessagesChange={(messages) => {
        if (messages && messages.length > 0) {
          const message = messages[messages.length - 1]
          if ('requires_bool_input' in message) {
            if (message.requires_bool_input) {
              setBoolResponse(true);
            } else {
              setBoolResponse(false);
            }
          }
        }
      }}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));

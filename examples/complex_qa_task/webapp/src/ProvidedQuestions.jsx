import React from "react";

function ProvidedQuestions({ providedQuestions }) {
    if (providedQuestions.length === 0) {
        return null;
    } else {
        return (
            <div>
                <h3>Provided Questions: </h3>
                {providedQuestions.map((question, index) => (
                    <div key={index}>
                        <p><b>{question}</b></p>
                    </div>
                ))}
                <hr style={{ borderTop: "1px solid #555" }} />
            </div>
        )
    }
}

export { ProvidedQuestions };
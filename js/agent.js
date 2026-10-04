async function runAgent() {

    const input = document.getElementById("goal");
    const result = document.getElementById("agentResult");
    const goal = input.value.trim();

    if (!goal) {
        result.innerHTML = "<p>Tell BUYGEN what you want to buy.</p>";
        return;
    }

    result.innerHTML = `
        <div class="flow">
            BUYGEN IS SEARCHING → COMPARING → RECOMMENDING...
        </div>
    `;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/agent/run",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    goal: goal
                })
            }
        );

        const data = await response.json();

        const products = data.candidates || [];

        if (products.length === 0) {

            result.innerHTML = `
                <div class="flow">
                    NO MATCHING PRODUCTS FOUND.
                </div>
            `;

            return;
        }

        result.innerHTML = `
            <div class="eyebrow">BUYGEN AI ANALYSIS</div>
            <h3 style="font-size:28px;font-weight:400">
                ${products.length} PRODUCTS MATCH YOUR GOAL
            </h3>

            <div class="product-grid">

                ${products.map(product => `

                    <article class="product">

                        <div class="product-img">
                            ${
                                product.image
                                ? `<img
                                    src="${product.image}"
                                    style="width:100%;height:190px;object-fit:contain;"
                                  >`
                                : "BUYGEN PRODUCT"
                            }
                        </div>

                        <div class="match">
                            ${product.agent_score || 0}% AI MATCH
                        </div>

                        <h3>
                            ${product.name}
                        </h3>

                        <p>
                            ${product.seller || "Marketplace"}
                            · ⭐ ${product.rating || "—"}
                        </p>

                        <div class="price">
                            ₹${product.price}
                        </div>

                        <a
                            href="${product.product_link}"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="product-link"
                        >
                            VIEW PRODUCT ↗
                        </a>

                    </article>

                `).join("")}

            </div>

            <div class="flow">
                BUYGEN RECOMMENDS THE HIGHEST-MATCH OPTION.
                HUMAN APPROVAL REQUIRED BEFORE TRANSACTION.
            </div>
        `;

    } catch (error) {

        console.error(error);

        result.innerHTML = `
            <div class="flow">
                BUYGEN BACKEND CONNECTION FAILED.
            </div>
        `;
    }
}

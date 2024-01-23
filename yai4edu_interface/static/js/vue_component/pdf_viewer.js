Vue.component("pdfPage", {
	template: `
		<div class="pdf-page-container" :id="getPageContainerID" :ref="getPageContainerID">
			<canvas class="pdf-canvas-layer" :id="getCanvasID" :ref="getCanvasID"></canvas>
			<div 
				class="pdf-text-layer" 
				:id="getTextLayerID" 
				:ref="getTextLayerID"
			></div>
		</div>
	`,
	props: {
		pageNumber: {
			type: Number,
			required: true
		},
		page: {
			type: Object,
			required: true
		},
		annotation_api: {
			type: String,
			required: true
		},
		scale: Number,
		pageContainerID: String,
		canvasID: String,
		isRenderText: Boolean,
		textLayerID: String
	},
	data() {
		return {
			viewport: null
		}
	},
	computed: {
		getPageContainerID() {
			const idString = this.pageContainerID || 'pdf-page-container'
			return idString + '-' + this.pageNumber
		},
		getCanvasID() {
			const idString = this.canvasID || 'pdf-canvas-layer-page'
			return idString + '-' + this.pageNumber
		},
		getTextLayerID() {
			const idString = this.textLayerID || 'pdf-text-layer-page'
			return idString + '-' + this.pageNumber
		}
	},
	methods: {
		async loadPage() {
			const canvas = this.$refs[this.getCanvasID]
			canvas.height = this.viewport.height
			canvas.width = this.viewport.width
			const context = canvas.getContext('2d')
			const renderContext = {
				canvasContext: context,
				viewport: this.viewport
			}
			await this.page.render(renderContext);
		},
		async loadTextLayer() {
			// console.log('loadTextLayer');
			const div = this.$refs[this.getTextLayerID]
			const textContent = await this.page.getTextContent()
			const textLayer = pdfjsLib.renderTextLayer({
				container: div,
				textContent,
				viewport: this.viewport
			})
			await textLayer._render();
			this.annotatePage();
		},
		annotatePage() {
			console.log('Annotating page', this.getTextLayerID);
			const div = this.$refs[this.getTextLayerID];
			const inner_text = remove_hyphenation(div.innerText).replace(/\n/g, '').replace(/  +/g, ' ');
			// console.log(inner_text);
			const self = this;

			for (const chunked_inner_text of stringToChunks(inner_text,5000))
			{
				$.ajax({
					type: "GET",
					url: self.annotation_api,
					responseType:'application/json',
					data: {
						'sentence': encodeURIComponent(chunked_inner_text), 
					},
					success: function (annotation_list) {
						console.log('annotation_list', annotation_list);
						div.innerHTML = annotate_html(div.innerHTML, chunked_inner_text, annotation_list, linkify, merge_span=true);
					},
					error: function(error) {
						console.log('Error:', error);
					},
				});
			}
		},
	},
	created() {
		this.viewport = this.page.getViewport({ scale: this.scale })
	},
	async mounted() {
		this.loadPage()
		if (this.isRenderText) {
			this.loadTextLayer()
		}
	}
});

Vue.component("vuePdfjsWrapper", {
	template: `
		<div class="pdf-pages-container" ref="pdf-pages-container">
			<div v-if="loading" class="d-flex align-items-center">
				<strong>Loading...</strong>
				<b-spinner class="ml-auto"></b-spinner>
			</div>

			<b-row v-if="!loading">
				<b-col class="text-left">
					<b-button v-if="currentPage > 1" v-on:click="currentPage--">&laquo; Prev</b-button>
				</b-col>

				<b-col cols="8" class="text-center">
					<b-row>
						<b-col class="text-right">
							Page
						</b-col>
						<b-col>
							<b-form-input type="number" v-model="currentPage" min="1" :max="pagesAmount" debounce="500"></b-form-input>
						</b-col>
						<b-col class="text-left">
							/{{pagesAmount}}
						</b-col>
					</b-row>
					<b-row>
						<b-form-input id="range-1" type="range" v-model="currentPage" min="1" :max="pagesAmount" debounce="500"></b-form-input>
					</b-row>
				</b-col>
				<b-col class="text-right">
					<b-button v-if="currentPage < pagesAmount" v-on:click="currentPage++">Next &raquo;</b-button>
				</b-col>
			</b-row>

			<pdf-page
				v-if="page" 
				:key="'pdf-canvas-layer-' + page.pageNum"
				:page-number="page.pageNum"
				:page="page"
				:scale="scale"
				:is-render-text="isRenderText"
				:annotation_api="annotation_api"
			/>

			<b-row v-if="!loading">
				<b-col class="text-left">
					<b-button v-if="currentPage > 1" v-on:click="currentPage--">&laquo; Prev</b-button>
				</b-col>
				<b-col cols="8" class="text-center"></b-col>
				<b-col class="text-right">
					<b-button v-if="currentPage < pagesAmount" v-on:click="currentPage++">Next &raquo;</b-button>
				</b-col>
			</b-row>

			<br>
		</div>
	`,
	
	props: {
		pdfSrc: null,
		scale: { type: Number, default: 2 },
		currentPage: { type: Number, default: 0 },
		pagesAmount: { type: Number, default: 0 },
		isSinglePage: { type: Boolean, default: false },
		isRenderText: { type: Boolean, default: true },
		loading: { type: Boolean, default: true },
	},
	data() {
		return {
			page: [],
			doc: null,
			annotation_api: GET_ANNOTATION_API,
		}
	},
	methods: {
		async loadDocument() {
			this.loading = true;
			console.log('Loading', this.pdfSrc);
			if (!this.pdfSrc) {
				console.warn('Please give me a PDF file source to feed pdfjsLib.getDocument()')
				return
			}
			this.page = null;
			this.doc = await pdfjsLib.getDocument(this.pdfSrc).promise;
			this.pagesAmount = this.doc.numPages;
			this.currentPage = 1;
			this.loadCurrentPage();
		},
		async loadCurrentPage() {
			const this_page_num = parseInt(this.currentPage);
			// this.loading = true;
			// console.log('isSinglePage', this.isSinglePage);
			// console.log('isRenderText', this.isRenderText);
			console.log('currentPage', this_page_num)

			// this.pages = []
			this.page = await this.doc.getPage(this_page_num);
			this.page.pageNum = this_page_num;

			// this.$emit('loaded')
			this.loading = false;
		},
		setCurrentPage(v) {
			this.currentPage = v;
		}
	},
	watch: {
		currentPage(value) {
			if (value >= 1 && value <=this.pagesAmount)
				this.loadCurrentPage();
		},
		pdfSrc(value) {
			if (value) {
				this.loadDocument();
			}
		},
		scale() {
			this.loadDocument()
		},
		isRenderText() {
			this.loadDocument()
		}
	},
	created() {
		if (this.pdfSrc) {
			this.loadDocument()
		}
	}
});


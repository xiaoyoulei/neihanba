package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"time"
)

type TextItem struct {
	Title string
	Data  string
	Time  int
}

type TextStruct struct {
	Items []TextItem
}

type TextModule struct {
	Data      [2]TextStruct
	filename  string
	reloadGap int
	nowidx    int
	modtime   time.Time
}

func (this *TextModule) Init() (err error) {
	this.filename = "./data/text.json"
	this.reloadGap = 600
	this.nowidx = 1
	this.modtime = time.Unix(0, 0)
	err = this.load()
	if err != nil {
		return
	}
	go this.reload()
	return
}

func (this *TextModule) load() (err error) {
	f, err := os.OpenFile(this.filename, os.O_RDONLY, 0777)
	if err != nil {
		fmt.Printf("open file [%s] fail. err[%s]\n", this.filename, err.Error())
		return err
	}
	tmp, err := f.Stat()
	if err != nil {
		fmt.Printf("stat file[%s] fail .err [%s]\n", this.filename, err.Error())
		return
	}
	if tmp.ModTime().Equal(this.modtime) {
		return
	}
	this.modtime = tmp.ModTime()
	data := make([]byte, 0)
	data, err = ioutil.ReadAll(f)
	index := 0
	if this.nowidx == 0 {
		index = 1
	}
	err = json.Unmarshal(data, &this.Data[index])
	if err != nil {
		fmt.Printf("unmarshal text json fail . err[%s]\n", err.Error())
		return
	}
	this.nowidx = index
	return
}

func (this *TextModule) reload() {
	for {
		time.Sleep(time.Duration(this.reloadGap) * time.Second)
		this.load()
	}
}

func (this *TextModule) Search(from int, delta int) (data []TextItem) {
	index := this.nowidx
	if from >= len(this.Data[index].Items) {
		return
	}
	d := 0
	for i := from; i < len(this.Data[index].Items) && d < delta; i++ {
		data = append(data, this.Data[index].Items[i])
		d++
	}
	return
}

var WorkModule *TextModule

func work(resp http.ResponseWriter, req *http.Request) {
	err := req.ParseForm()
	if err != nil {
		resp.WriteHeader(http.StatusBadRequest)
		return
	}
	fromstr := req.Form["from"]
	deltastr := req.Form["delta"]
	if len(fromstr) == 0 || len(deltastr) == 0 {
		resp.WriteHeader(http.StatusBadRequest)
		return
	}
	from, err := strconv.Atoi(fromstr[0])
	delta, err := strconv.Atoi(deltastr[0])
	data := make([]TextItem, 0)
	data = WorkModule.Search(from, delta)
	ret, err := json.Marshal(data)
	if err != nil {
		resp.WriteHeader(http.StatusOK)
		return
	}
	resp.WriteHeader(http.StatusOK)
	resp.Write(ret)
	return
}

func main() {
	WorkModule = &TextModule{}
	if WorkModule.Init() != nil {
		fmt.Errorf("init workModule fail \n")
		return
	}
	http.HandleFunc("/text", work)
	err := http.ListenAndServe(":8832", nil)
	if err != nil {
		fmt.Errorf("start server fail . err[%s]", err.Error())
	}
	return
}
